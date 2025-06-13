# -*- coding: utf-8 -*-
import argparse
from particleanalyzer.app import main as run_app

def main():
    parser = argparse.ArgumentParser(description='Particle Analyzer')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Команда run
    run_parser = subparsers.add_parser('run', help='Run the application')
    run_parser.set_defaults(func=run_app)
    
    args = parser.parse_args()
    args.func()

if __name__ == "__main__":
    main()