from app import create_app

app = create_app()

if __name__ == '__main__':
    # change host to 0.0.0.0 if you want external access
    app.run(debug=True, port=5000)