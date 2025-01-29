from abc import ABC, abstractmethod
import logging
import pkgutil
import tempfile
from pathlib import Path

from . import external_exec as execute


def dbgbench_dir() -> Path:
    """
    Return the path to the dbgbench directory.
    Raises an AssertionError if it does not exist.
    """
    dbgbench = (Path(__file__).parent / ".." / ".." / ".." / ".." / "dbgbench.github.io").resolve()
    if not dbgbench.exists():
        raise AssertionError(
            "You need to check out dbgbench to the correct location if you want to run dbgbench subjects."
        )
    return dbgbench

RESOURCE_DIR = (Path(__file__).parent.parent / "resources").resolve()


class AbstractContainer(ABC):
    """
    Minimal abstraction for a Docker container used in dbgbench.
    """

    def __init__(self, image_name: str, container_name: str):
        self._image_name = image_name
        self._container_name = container_name
        self._running = False

    @abstractmethod
    def create_image(self) -> None:
        """
        Build (or otherwise obtain) the Docker image if it does not already exist.
        """
        pass

    @abstractmethod
    def start(self, username: str = "root") -> None:
        """
        Start the container with the specified user context.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the container if it is running.
        """
        pass

    def __enter__(self):
        # Default context manager usage
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop container at context exit
        self.stop()

    @property
    def name(self) -> str:
        """
        Returns the container name.
        """
        return self._container_name

    def run_in_container(self, cmd: list[str], cwd: Path = None) -> bytes:
        """
        Execute a command within the container and return its stdout as bytes.
        """
        if not self._running:
            raise RuntimeError("Cannot run command. Container is not running.")

        full_cmd = ["docker", "exec"]
        if cwd:
            full_cmd += ["-w", str(cwd)]
        full_cmd += [self._container_name] + cmd
        return execute.check_output(full_cmd)

    def copy_into(self, local_paths: list[Path], dst_path: Path, username: str = "root") -> None:
        """
        Copy files or directories from the host into the container. Adjust ownership after copy.
        """
        if not self._running:
            raise RuntimeError("Cannot copy files. Container is not running.")

        for lp in local_paths:
            execute.run(
                [
                    "docker", "cp", str(lp.resolve()),
                    f"{self._container_name}:{str(dst_path)}/"
                ],
                None, check=True
            )

        # Fix ownership (optional if not needed)
        execute.run(
            [
                "docker", "exec", "-u", "root", self._container_name, "chown", "-R",
                f"{username}:{username}", str(dst_path)
            ],
            None, check=False
        )


class Container(AbstractContainer):
    """
    A generic Docker container that builds from a local Dockerfile in `basedir`.
    """

    def __init__(self, basedir: Path, container_name: str):
        """
        :param basedir: Path that contains a Dockerfile for building the image.
        :param container_name: The name of the running container instance.
        """
        basedir = basedir.resolve()
        super().__init__(image_name=basedir.name, container_name=container_name)
        self._basedir = basedir

    def create_image(self) -> None:
        """
        If the Docker image does not exist locally, build it via `docker build`.
        """
        existing = execute.check_output(['docker', 'images', '-q', self._image_name])
        if not existing:
            logging.info(f"Building Docker image '{self._image_name}' from {self._basedir}...")
            execute.run(["docker", "build", "-t", self._image_name, "."],
                        None, cwd=str(self._basedir))
        else:
            logging.info(f"Using existing Docker image '{self._image_name}' with ID {existing.strip()}")

    def start(self, username: str = "root") -> None:
        """
        Create the image (if necessary) and then run a container from it.
        Optionally copy default scripts into the container.
        """
        self.create_image()
        logging.info(f"Starting container '{self._container_name}' from image '{self._image_name}'...")
        proc = execute.run(
            ["docker", "run", "-dt", "--name", self._container_name, self._image_name],
            None
        )
        proc.check_returncode()
        self._running = True

        # Optionally copy default Python scripts into /root/Desktop/alhazen_scripts (or home/username)
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir, "alhazen")
            scripts_dir.mkdir(parents=True, exist_ok=True)

            # Example: copying some "framework" scripts
            needed_files = ["helpers.py", "oracles.py", "external_exec.py"]
            for fname in needed_files:
                data = pkgutil.get_data("dbgbench.framework", fname)
                if data is None:
                    continue
                (scripts_dir / fname).write_bytes(data)

            self.copy_into(
                [scripts_dir],
                self.container_root_dir(username) / "alhazen_scripts",
                username=username
            )

        logging.info(f"Container '{self._container_name}' is running.")

    def stop(self) -> None:
        """
        Kill and remove the running container.
        """
        if self._running:
            logging.info(f"Stopping container '{self._container_name}'...")
            kill_out = execute.check_output(["docker", "kill", self._container_name])
            logging.info(f"Kill result: {kill_out}")
            rm_out = execute.check_output(["docker", "rm", self._container_name])
            logging.info(f"Remove result: {rm_out}")
            self._running = False

    def container_root_dir(self, username: str = "root") -> Path:
        """
        Return the home directory for the specified user in the container.
        """
        if username == "root":
            return Path("/root/Desktop/")
        return Path(f"/home/{username}/")


class DBGBenchContainer(Container):
    """
    A specialized container that extends the generic Container with
    DBGBench-specific logic (creating ephemeral containers, etc.).
    """

    def __init__(self, subject: str, container_name: str):
        """
        :param subject: e.g. "grep", "find", etc.
                        We'll look for a directory named 'alhazen_<subject>' for the build context.
        :param container_name: The name for the running container instance.
        """
        super().__init__(
            basedir=Path(f"alhazen_{subject}"),
            container_name=container_name
        )
        self._subject = subject

    def create_image(self) -> None:
        """
        Override: DBGBench may have a different procedure to create (or re-create)
        the Docker image.
        """
        image_name = f"alhazen_{self._subject}"
        existing = execute.check_output(['docker', 'images', '-q', image_name])
        if not existing:
            logging.info(f"[DBGBench] Re-creating the image '{image_name}' for subject '{self._subject}'...")

            # Start an "original" ephemeral container for setup
            ephemeral_name = f"{self._container_name}_orig"
            cmd = ["bash", "run.sh", self._subject, ephemeral_name, "exit"]
            self._running = True
            # run.sh presumably lives in dbgbench_dir()/docker
            docker_dir = dbgbench_dir() / "docker"
            execute.run(cmd, None, cwd=str(docker_dir))

            # Copy in a setup script to ephemeral container
            self.copy_into_orig(
                [RESOURCE_DIR / "machine_setup.sh"],
                self.container_root_dir("root")
            )

            # Execute that script
            execute.run(
                [
                    "docker", "exec", ephemeral_name,
                    "bash", str((self.container_root_dir("root") / "machine_setup.sh").resolve())
                ],
                None,
                check=True
            )

            # Stop ephemeral
            execute.run(["docker", "kill", ephemeral_name], None, check=True)
            self._running = False

            # Commit ephemeral container into a new local image
            execute.run(['docker', 'commit', ephemeral_name, image_name], None, check=True)
            # Remove ephemeral container
            execute.run(['docker', 'rm', ephemeral_name], None, check=True)
        else:
            logging.info(f"[DBGBench] Image '{image_name}' already exists (ID: {existing.strip()}).")

    def copy_into_orig(self, files: list[Path], targetdir: Path) -> None:
        """
        Helper to copy into the ephemeral container named '{self.name}_orig'
        rather than the main container.
        """
        ephemeral_name = f"{self.name}_orig"
        for local_path in files:
            execute.run(
                [
                    "docker", "cp",
                    str(local_path.resolve()),
                    f"{ephemeral_name}:{targetdir.resolve()}/"
                ],
                None, check=True
            )

    def check_output(self, cmd, cwd=None):
        if not self._running:
            raise AssertionError("Machine is stopped already.")
        full_cmd = ["docker", "exec"]
        if cwd is not None:
            full_cmd = full_cmd + ["-w", cwd]
        full_cmd = full_cmd + [self.name] + cmd
        return execute.check_output(full_cmd)
