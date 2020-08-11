from nottingtable import create_app

app = create_app(development_config=False)

if __name__ == '__main__':
    app.run()
