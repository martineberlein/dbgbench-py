#!/usr/bin/env bash

clang -E grep.bnf.c | grep -v "^#" > grep.bnf
clang -E find.bnf.c | grep -v "^#" > find.bnf
