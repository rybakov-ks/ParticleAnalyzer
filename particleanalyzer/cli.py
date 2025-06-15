# -*- coding: utf-8 -*-
import argparse
from particleanalyzer.app import main as run_app

def main():
    parser = argparse.ArgumentParser(description='Particle Analyzer')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    run_parser = subparsers.add_parser('run', help='Run the application')
    run_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to run the application on (default: 8000)'
    )
    run_parser.set_defaults(func=run_app)
    
    args = parser.parse_args()
    args.func(port=args.port)

if __name__ == "__main__":
    main()