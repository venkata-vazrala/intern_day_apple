# Dashboard UI Guide

## 🎨 UI Overview

A beautiful, modern web dashboard for the Automation Build & Test Tracker with a dark Apple-inspired design.

## 🚀 Access the Dashboard

```bash
# Start the server
python manage.py runserver 8001

# Open in browser
http://127.0.0.1:8001/
```

## 📱 Features

### 1. **Dashboard View** (Home)
- **Statistics Cards**: 
  - Total Pipelines
  - Total Runs
  - Active Runs
  - Average Score
- **Recent Runs**: List of 5 most recent runs with completion progress
- **Pipeline Overview**: Quick view of configured pipelines

### 2. **Pipelines View**
- View all configured pipelines
- See pipeline details (stages, substages, weights)
- Click on any pipeline to see full configuration
- Shows:
  - Pipeline name and description
  - Number of stages
  - Version and project information

### 3. **Runs View**
- Complete list of all runs
- Filter by pipeline or status
- Click on any run to see detailed breakdown
- Shows:
  - Run ID and trigger source
  - Overall completion score
  - Status (running, completed, failed)
  - Progress bar visualization
  - Start time

### 4. **Trends View**
- Visual chart showing score progression over time
- Select pipeline from dropdown
- Line chart with last 10 runs
- Track improvement/regression

### 5. **Create New Run**
- Click "New Run" button in top bar
- Select pipeline
- Enter trigger source (e.g., "Jenkins", "Manual Test")
- Creates run with all stages/substages initialized

## 🎯 Interactive Elements

### Run Details Modal
Click any run to see:
- Full stage and substage breakdown
- Completion percentage for each stage
- Status badges (completed, running, pending)
- Triggered by information
- Timeline

### Pipeline Details Modal
Click any pipeline to see:
- Complete stage configuration
- Substage weights and types (manual/auto)
- Definition of Done for each substage
- Validation types

## 🎨 Design Features

- **Dark Theme**: Apple-inspired dark UI
- **Responsive**: Works on desktop and mobile
- **Smooth Animations**: Hover effects and transitions
- **Color-Coded Statuses**:
  - 🟢 Green: Completed
  - 🟡 Orange: Running/Partial
  - 🔵 Blue: Info/Pending
  - 🔴 Red: Failed
- **Progress Bars**: Visual representation of completion
- **Real-time Updates**: Refresh button to reload data

## 🔄 Navigation

- **Dashboard** 📊: Overview and statistics
- **Pipelines** 🗂️: Browse all pipeline configurations
- **Runs** ▶️: View all execution runs
- **Trends** 📈: Analyze performance over time

## 💡 Tips

1. **Quick Refresh**: Click the refresh button (🔄) in the top bar
2. **View Details**: Click on any card/item to see full details
3. **Create Runs**: Use the "New Run" button to trigger new executions
4. **Track Trends**: Select a pipeline in Trends view to see historical performance
5. **Mobile Friendly**: Sidebar collapses on smaller screens

## 🎬 Demo Flow

1. **Start at Dashboard**: See overall statistics
2. **View Pipelines**: Check configured pipelines and their stages
3. **Create a Run**: Click "New Run" and select a pipeline
4. **Monitor Progress**: Go to Runs view to see the new run
5. **Analyze Trends**: Use Trends view to see performance over time

## 🛠️ Technical Details

- **Frontend**: Vanilla JavaScript (no framework dependencies)
- **Charts**: Chart.js for trend visualization
- **Icons**: Font Awesome
- **Styling**: Custom CSS with CSS variables
- **API**: Consumes Django REST Framework endpoints
- **Real-time**: Fetches live data from `/api/` endpoints

## 📊 API Integration

The UI automatically calls:
- `GET /api/pipelines/` - List pipelines
- `GET /api/runs/` - List runs
- `GET /api/runs/{id}/summary/` - Run details
- `GET /api/pipelines/{id}/trend/?n=10` - Trend data
- `POST /api/runs/` - Create new run

## 🎨 Color Scheme

```
Primary Blue:   #007AFF (Apple Blue)
Success Green:  #34C759 (Apple Green)
Warning Orange: #FF9500 (Apple Orange)
Danger Red:     #FF3B30 (Apple Red)
Dark Background: #1C1C1E
Card Background: #2C2C2E
Sidebar: #000000
```

## 🚀 Future Enhancements

- [ ] Real-time updates via WebSockets
- [ ] Manual substage status updates from UI
- [ ] Export reports (PDF/CSV)
- [ ] User authentication and permissions
- [ ] Custom dashboard layouts
- [ ] Notification system
- [ ] Dark/Light theme toggle
- [ ] Advanced filtering and search
- [ ] Pipeline comparison view

## 📸 Screenshots

Access the dashboard at http://127.0.0.1:8001/ to see:
- Modern dark UI with sidebar navigation
- Interactive cards with hover effects
- Beautiful progress bars and badges
- Responsive modals for detailed views
- Trend charts with smooth animations

---

**Enjoy your beautiful tracking dashboard!** 🎉
