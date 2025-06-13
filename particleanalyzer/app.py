# -*- coding: utf-8 -*-
import os
from particleanalyzer.core.ui import create_interface
from particleanalyzer.core.languages import i18n

example_path = os.path.join(os.path.dirname(__file__), "assets", "example")

def main():
    demo = create_interface()
    demo.queue(
        default_concurrency_limit=5,
        api_open=False
    ).launch(
        server_name="127.0.0.1",
        server_port=8000,
        pwa=True,
        favicon_path="particleanalyzer/assets/icon/search-solid.png",
        i18n=i18n,
        allowed_paths=[example_path]
    )
