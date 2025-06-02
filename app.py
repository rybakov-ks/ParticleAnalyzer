from core.ui import create_interface

def main():
    demo = create_interface()
    demo.queue(
        default_concurrency_limit=5,
        api_open=False
    ).launch(
        server_name="127.0.0.1",
        server_port=8000,
        pwa=True,
        favicon_path="assets/icon/search-solid.png",
    )

if __name__ == "__main__":
    main()