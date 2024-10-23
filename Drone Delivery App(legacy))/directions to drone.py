# drone_delivery_app/ - This is the root folder for your project.

# ├── app.py - This file contains the Flask application logic. It is responsible for handling the backend.
#              Here, you define routes and the core functionality for the drone delivery system.
#              The app interacts with the front-end through these routes and processes user inputs.

# ├── templates/ - This folder contains HTML templates. In Flask, HTML files are stored in the 'templates' folder
#                  and are used to render the user interface (UI) dynamically.

# │   └── index.html - The main HTML file for the drone delivery system’s UI.
#                      This file is rendered when the user visits the homepage.
#                      It contains a form for users to input delivery details (destination, package weight, etc.).

# ├── static/ - This folder stores static files like CSS and images.
#               Flask automatically serves files from this folder.

# │   └── style.css - The CSS file to style the HTML pages and create a more visually appealing user interface.

# └── venv/ - Virtual environment folder (optional but recommended). It isolates project dependencies (e.g., Flask, other Python packages),
#             ensuring they do not conflict with other projects on your machine.
#             This environment is activated whenever you are working on this project.
