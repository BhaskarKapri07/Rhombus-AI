# Rhombus-AI Data Type Inference Tool

A web application that processes and displays data, focusing on data type inference and conversion for datasets using Python, Django, and React.

## Project Structure
```
data-type-inference/
├── backend/               # Django backend
│   ├── config/           # Project settings
│   ├── data_processor/   # Main application
│   │   ├── api/         # API endpoints
│   │   └── services/    # Business logic
│   ├── requirements.txt
│   └── manage.py
└── frontend/             # React frontend
    ├── src/
    │   ├── components/  # React components
    │   ├── services/    # API services
    │   └── types/       # TypeScript types
    └── package.json
```

## Features

- Upload CSV and Excel files
- Automatic data type inference
- Interactive data type override
- Preview data in tabular format
- Support for various data types:
  - Integer (with null support)
  - Decimal
  - Date/Time
  - Boolean
  - Category
  - Text

## Technology Stack

- **Backend:**
  - Python 3.x
  - Django
  - Django REST Framework
  - Pandas
  - NumPy

- **Frontend:**
  - React
  - TypeScript
  - Mantine UI
  - Axios

## Setup Instructions

### Clone Repository

```bash
# Clone the repository
git clone https://github.com/BhaskarKapri07/Rhombus-AI.git

# Navigate to project directory
cd Rhombus-AI
```

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. Start both backend and frontend servers
2. Open `http://localhost:5173` in your browser
3. Upload a CSV or Excel file using the drag-and-drop interface
4. View the inferred data types and preview data
5. Use the dropdown menus to override data types if needed
6. Click "Apply Changes" to update the data types

## API Endpoints

### POST /api/process-file/
Upload and process a file.
- Input: CSV or Excel file (multipart/form-data)
- Output: 
```json
{
  "column_types": {
    "column_name": "data_type"
  },
  "preview_data": [
    {...}
  ]
}
```

### POST /api/update-types/
Update data types for columns.
- Input:
```json
{
  "column_types": {
    "column_name": "new_data_type"
  },
  "preview_data": [
    {...}
  ]
}
```
- Output: Updated data with new types

## Supported Data Types

- `Int64`: Integer values (null-capable)
- `float64`: Decimal numbers
- `datetime64[ns]`: Date and time values
- `bool`: Boolean values
- `category`: Categorical data
- `object`: Text or mixed content

## Error Handling

The application handles various error cases:
- Invalid file types
- File size limitations
- Data type conversion errors
- Server communication errors

