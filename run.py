from app import create_app
import os
app = create_app()
# in create_app() or before first request
app.jinja_env.globals.update(enumerate=enumerate)

if __name__ == '__main__':
    # change host to 0.0.0.0 if you want external access
    import os
    from dotenv import load_dotenv
    load_dotenv()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)