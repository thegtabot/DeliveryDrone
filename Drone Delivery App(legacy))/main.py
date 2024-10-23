# Flask app (backend)


from flask import Flask, render_template, request

app = Flask(__name__)

# Drone tracking logic can be placed here if needed
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track_package():
    package_id = request.form.get('package_id')
    # Add your package tracking logic here
    return f'Tracking result for package ID: {package_id}'

if __name__ == '__main__':
    app.run(debug=True)

