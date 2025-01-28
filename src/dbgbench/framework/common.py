from pathlib import Path
import pandas
import subprocess
import logging
import io
from time import perf_counter
import uuid

from abc import abstractmethod, ABCMeta

from .bug_class import Bug
from . import docker, external_exec as execute


RESOURCE_DIR = Path(__file__).parent.parent / "resources"


def dbgbench_dir():
    """returns the path to the dbgbench directory"""
    dbgdir = Path(__file__).parent / ".." / ".." / ".." / ".." / "dbgbench.github.io"
    print(dbgdir)
    if not dbgdir.exists():
        raise AssertionError("You need to check out dbgbench to the correct location if you want to run dbgbench subjects.")
    return dbgdir


class DbgbenchBug(Bug, metaclass=ABCMeta):

    def __init__(self, bugnr, oracle):
        self.__identifier = bugnr
        self.__oracle = oracle
        self.__container = None

    def container(self):
        return self.__container

    @abstractmethod
    def _container_setup(self):
        pass

    @abstractmethod
    def _sample_runner(self):
        pass

    def subject(self) -> str:
        return self.__identifier

    def sample_files(self):
        subject = self.subject()
        subject = subject[:subject.rfind(".")]
        yield Path(__file__).parent.parent / "resources" / "samples" / f"{self.subject()}.cli"
        yield Path(__file__).parent.parent / "resources" / "samples" / f"{subject}.benign.cli"

    def tear_down(self):
        logging.info("tear down DBGBenchBug")
        if self.__container is not None:
            self.__container.stop()

    def __check_container(self):
        if self.__container is None:
            subject = self.subject()
            subject = subject[:subject.rfind(".")]
            name = "dbgbench_{bug}".format(bug=self.subject())
            self.__container = DBGBenchContainer(subject, "{name}_{id}".format(name=name, id=uuid.uuid4()))
            self.__container.start()
            self._container_setup()

    def execute_sample_list(self, execdir, samples):
        self.__check_container()
        if 0 != len(list(samples)):
            self.__container.check_output(["mkdir", "-p", (self.__container.container_root_dir("root") / "alhazen_samples/samples/").resolve()])
            self.__container.copy_into(samples, self.__container.container_root_dir("root") / "alhazen_samples/samples/", username="root")
            return self.__execute_in_container(execdir)
        else:
            return pandas.DataFrame(columns=["file", "line", "subject", "return code", "output", "oracle"])

    def __execute_in_container(self, execdir):
        output = b""
        try:
            output = self.__container.check_output(["python3",
                                                    self._sample_runner(),
                                                    self.subject(),
                                                    (self.__container.container_root_dir("root") / "alhazen_samples/samples/").resolve(), "rm"])
            prefix = "# csv #- "
            text = output.decode()
            lines = [line[len(prefix):] for line in text.split('\n') if line.startswith(prefix)]
            df = pandas.read_csv(io.StringIO("\n".join(lines)), keep_default_na=False, lineterminator='\n')
            df["oracle"] = df.apply(lambda r: self.__oracle.apply_oracle(self, r), axis=1)
            return df
        except subprocess.CalledProcessError as ex:
            logging.exception("Process failed")
            logging.error(ex.output)
            raise
        except pandas.errors.ParserError:
            datafile = execdir / "errordata.csv"
            with open(datafile, 'wb') as df:
                df.write(output)
            logging.error(f"Parser error. Data is in {datafile}")
            raise
        except:
            logging.exception("Process failed")
            logging.error(output.decode())
            raise

    def execute_samples(self, sample_dir):
        self.__check_container()
        logging.info("Executing samples in {}".format(sample_dir))
        if 0 != len(list(sample_dir.iterdir())):
            self.__container.copy_into([sample_dir], self.__container.container_root_dir("root") / "alhazen_samples")
            return self.__execute_in_container(sample_dir)
        return pandas.DataFrame(columns=["file", "line", "subject", "return code", "output", "oracle"])

    def revision(self, basedir):
        return execute.check_output(["git", "rev-parse", "HEAD"],
                                    cwd=str(self.bug_dir(basedir) / self.subject())).decode().strip()

    def bug_dir(self, basedir):
        i = 1
        while True:
            check = basedir / "{subj}{i}".format(subj=self.subject(), i=i)
            if check.exists():
                id_file = check / self.identifier()
                if id_file.exists():
                    return check
            else:
                raise AssertionError("I could not find {subj} for {iden} (round: {i}, looking in {basedir})".format(
                    subj=self.subject(),
                    iden=self.identifier(),
                    i=i,
                    basedir=basedir))
            i = i + 1

    def grammar_file(self):
        subject = self.subject()
        subject = subject[:subject.rfind(".")]
        # find the grammar file
        grammar_file = Path(__file__).parent.parent / "resources" / (subject + ".bnf")
        if not grammar_file.exists():
            execute.check_output(["bash", "create_grammars.sh"], cwd=Path(__file__).parent.parent / "resources" )
            if not grammar_file.exists():
                raise AssertionError(f"File {grammar_file} does not exist!")
        return grammar_file

    def apply_oracle_single(self, row):
        return self.__oracle.apply_oracle(self, row)

    def apply_oracle(self, data):
        bug_data = data[data['subject'] == self.identifier()].copy()
        bug_data['oracle'] = bug_data.apply(lambda r: str(self.apply_oracle_single(r)), axis=1)
        return bug_data

    def execute_sample(self, cli, line):
        subjpath = self.locate_executable(self.__container.container_root_dir("root"))
        start = perf_counter()
        rc, output = self.execute_cli_with_executable(line, subjpath)
        runtime = perf_counter() - start
        return rc, output, runtime

    def generate_oracle_data(self, cli):
        return self.__oracle.generate_oracle_data(self, cli)


class DBGBenchContainer(docker.Container):

    def __init__(self, subject, name):
        self.__subject = subject
        super(DBGBenchContainer, self).__init__(Path("alhazen_{}".format(subject)), name)

    def start(self, username="root"):
        super().start(username=username)
        # TODO you may want to add the git commit to the image name, just to be sure you have the latest version of the image.
        logging.info(f"Container {self.name} for {self.__subject} is running")

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("close DBGBenchContainer")
        self.stop()
        if self.__running:
            logging.info("close orig DBGBenchContainer")
            name = f"{self.name}_orig"
            logging.info("Stopping container {}".format(name))
            killout = execute.check_output(["docker", "kill", name])
            logging.info(f"Kill: {killout}")
            rmout = execute.check_output(["docker", "rm", name])
            logging.info(f"rm: {rmout}")
            self.__running = False

    def create_image(self):
        # check whether the image exists
        output = execute.check_output(['docker', 'images', '-q', "alhazen_{}".format(self.__subject)])
        if 0 == len(output):
            logging.info("Re-creating the image...")
            # it does not exist, so, create it
            # start the original dbgbench container
            name = f"{self.name}_orig"
            cmd = ["bash", "run.sh", self.__subject, name, "exit"]
            self.__running = True
            execute.run(cmd, None, cwd=str(dbgbench_dir() / "docker"))
            print(name, self.__subject)
            # install stuff in the image
            self.copy_into_orig([
                RESOURCE_DIR / "machine_setup_new.sh"], self.container_root_dir("root"))
            print(RESOURCE_DIR / "machine_setup_new.sh")
            execute.run(["docker", "exec", name, "bash", (self.container_root_dir("root") / "machine_setup_new.sh").resolve()], None, check=True)
            # stop the container
            execute.run(['docker', 'kill', name], None, check=True)
            self.__running = False
            # commit the image
            execute.run(['docker', 'commit', name, f"alhazen_{self.__subject}"], None, check=True)
            # and destroy the container
            execute.run(['docker', 'rm', name], None, check=True)

    def copy_into_orig(self, files, targetdir):
        name = self.name
        name = "{}_orig".format(name)
        for file in files:
            execute.run(["docker", "cp", str(file.resolve()), "{name}:{path}/"
                        .format(name=name, path=str(targetdir.resolve()))], None, check=True)
