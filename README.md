# Image-Repository

## Application Overview

This Flask web application allows users to upload, browse, and manage images with associated metadata. The primary features include uploading images with metadata, browsing images, viewing detailed image information, and downloading images. Additionally, the application includes a help page to guide users on how to use the various features.

## Key Features

1. **Image Uploading**:
    - Users can upload images in common formats (PNG, JPG, JPEG, GIF).
    - Each image upload requires additional metadata: part number, version, owner, category, and marking.
    - A unique identifier (UID) is generated for each image upon upload.

2. **Metadata Management**:
    - The application captures and stores metadata for each image, including filename, upload date, part number, version, owner, category, marking, and UID.
    - Metadata helps in organizing and searching for images efficiently.

3. **Browsing and Searching**:
    - Users can browse all uploaded images and filter them based on metadata fields such as part number and version.
    - A search bar allows users to enter queries to find specific images based on their metadata.

4. **Viewing and Downloading Images**:
    - Users can view images in a new window with a detailed display of their metadata.
    - A download button is available in the image view window to allow users to download the image.

5. **Help Page**:
    - A help page provides detailed instructions on how to use the application, including how to upload, browse, and manage images.

## Technical Components

1. **Flask**:
    - A lightweight web framework used to build the application.
    - Handles routing, request handling, and template rendering.

2. **Flask-SQLAlchemy**:
    - An ORM (Object-Relational Mapper) used to interact with the database.
    - Manages the `ImageMetadata` model, which stores image metadata.

3. **WTForms and Flask-WTF**:
    - Libraries used for form handling and validation.
    - Ensures that only valid image files are uploaded and required metadata fields are filled.

4. **Flask-Migrate**:
    - Manages database migrations using Alembic.
    - Allows for easy updates and changes to the database schema.

5. **Gunicorn**:
    - A WSGI HTTP server for deploying the application in a production environment.

## Detailed Functionality

### Image Uploading

- **Route**: `/upload`
- **Template**: `upload.html`
- **Function**: `upload()`
- **Description**: This route renders a form where users can select an image to upload and provide necessary metadata. Upon submission, the form data is validated, and the image is saved to the specified upload directory. Metadata, including a generated UID, is stored in the database.

### Browsing and Searching Images

- **Route**: `/browse`
- **Template**: `browse.html`
- **Function**: `browse()`
- **Description**: This route allows users to browse all uploaded images or search for images based on part number or version. The results are displayed with links to view each image in detail.

### Viewing and Downloading Images

- **Route**: `/view_image/<filename>`
- **Template**: `view_image.html`
- **Function**: `view_image(filename)`
- **Description**: This route displays an image in a new window along with its metadata. A download button is provided to allow users to download the image.

- **Route**: `/download/<filename>`
- **Function**: `download_file(filename)`
- **Description**: This route enables users to download the specified image file.

### Help Page

- **Route**: `/help`
- **Template**: `help.html`
- **Function**: `help()`
- **Description**: This route renders the help page, which provides detailed instructions on how to use the application.

## Application Usage

1. **Uploading Images**:
    - Go to the Upload page.
    - Select an image file and fill in the required metadata fields.
    - Click the "Upload" button to save the image and its metadata.

2. **Browsing and Searching Images**:
    - Go to the Browse page.
    - Enter a query in the search bar to filter images by part number or version, or leave it empty to see all images.
    - Click on a filename to view the image in detail.

3. **Viewing and Downloading Images**:
    - Click on a filename link to open the image in a new window.
    - In the new window, view the image and its metadata.
    - Click the "Download" button to download the image.

4. **Help Page**:
    - Go to the Help page for detailed instructions on using the application.

This documentation provides a comprehensive overview of the application's features, technical components, and usage instructions, ensuring users can effectively utilize the application for managing images and their metadata.
