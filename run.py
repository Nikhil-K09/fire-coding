from app import create_app

app = create_app()
# in create_app() or before first request
app.jinja_env.globals.update(enumerate=enumerate)

if __name__ == '__main__':
    # change host to 0.0.0.0 if you want external access
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )