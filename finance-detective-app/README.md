# 🕵️ Finance Detective - Angular Web App

An engaging, gamified financial education web application with a detective theme. Solve financial mysteries, earn badges, and become a legendary financial detective!

## 🎯 Features

### 🎮 Gamification
- **Detective Ranks**: Progress from Rookie to Legendary Detective
- **XP System**: Earn points by solving cases
- **Badges & Achievements**: Collect rewards for your accomplishments
- **Streak System**: Maintain daily investigation streaks
- **Perfect Scores**: Track your flawless case solutions

### 🕵️ Detective Theme
- **Case Files**: Financial concepts presented as detective cases
- **Evidence Board**: Visual history of your investigations
- **Detective HQ**: Your command center dashboard
- **Detective Noir Aesthetic**: Modern dark theme with gold accents

### 📱 Responsive Design
- Mobile-first approach
- Smooth animations and transitions
- Interactive UI elements
- Cross-browser compatibility

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18 or higher)
- **npm** (v9 or higher)
- **Angular CLI** (v17)
- **Python MCP Server** (running on port 8000)

### Installation

1. **Navigate to the app directory**:
   ```bash
   cd finance-detective-app
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Install Angular CLI globally** (if not already installed):
   ```bash
   npm install -g @angular/cli
   ```

### Running the Application

1. **Start the MCP Server** (in the parent directory):
   ```bash
   cd ..
   python mcp_server.py
   ```
   The server will run on `http://localhost:8000`

2. **Start the Angular app** (in a new terminal):
   ```bash
   cd finance-detective-app
   npm start
   ```
   The app will open at `http://localhost:4200`

3. **Open your browser** and navigate to:
   ```
   http://localhost:4200
   ```

## 📁 Project Structure

```
finance-detective-app/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── login/              # User onboarding
│   │   │   ├── dashboard/          # Detective HQ
│   │   │   ├── quiz/               # Case investigation
│   │   │   ├── evidence-board/     # Quiz history
│   │   │   ├── case-files/         # All cases
│   │   │   └── profile/            # User profile
│   │   ├── services/
│   │   │   └── mcp.service.ts      # API integration
│   │   ├── models.ts               # TypeScript interfaces
│   │   ├── app.module.ts           # App configuration
│   │   └── app.component.*         # Root component
│   ├── environments/               # Environment configs
│   ├── assets/                     # Images, fonts
│   ├── styles.css                  # Global styles
│   └── index.html                  # Entry point
├── angular.json                    # Angular configuration
├── package.json                    # Dependencies
├── tsconfig.json                   # TypeScript config
└── README.md                       # This file
```

## 🎨 Theme Customization

The app uses CSS custom properties for easy theming. Edit `src/styles.css`:

```css
:root {
  --primary-dark: #1a1a2e;
  --accent-gold: #f4a261;
  --accent-blue: #2a9d8f;
  /* ... more colors */
}
```

## 🔌 API Integration

The app communicates with the MCP Server via the `McpService`:

### Endpoints Used

- `GET /api/user/profile` - Get user profile
- `POST /api/user/profile` - Create/update profile
- `GET /api/user/gamification` - Get gamification data
- `POST /api/user/gamification/update` - Update points/badges
- `GET /api/user/quiz-history` - Get quiz history
- `POST /api/user/quiz-history` - Save quiz results
- `GET /api/user/transactions` - Get transaction data

### Configuration

API URL is configured in `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  mcpApiUrl: 'http://localhost:8000/api'
};
```

## 🎯 User Journey

1. **Welcome Screen** (Login Component)
   - Enter detective name
   - Select age, hobbies, interests
   - Create profile

2. **Detective HQ** (Dashboard)
   - View stats (points, streak, badges)
   - See available cases
   - Check progress to next rank

3. **Case Investigation** (Quiz Component)
   - Read detective story
   - Answer questions
   - Earn rewards

4. **Evidence Board** (History)
   - View past investigations
   - Track performance
   - See improvement trends

5. **Profile**
   - View all achievements
   - Check badge collection
   - Review stats

## 🏗️ Development

### Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
ng lint
```

### Adding New Components

```bash
ng generate component components/your-component
```

### Adding New Services

```bash
ng generate service services/your-service
```

## 🎮 Detective Ranks

| Rank | Points Required | Badge |
|------|----------------|-------|
| Rookie Detective | 0 | 🔍 |
| Junior Detective | 100 | 🕵️ |
| Detective | 250 | 🎯 |
| Senior Detective | 500 | 🏆 |
| Chief Detective | 750 | 👑 |
| Legendary Detective | 1000+ | ⭐ |

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 4200
lsof -ti:4200 | xargs kill -9

# Or use a different port
ng serve --port 4201
```

### MCP Server Not Running

Ensure the MCP server is running:
```bash
cd ..
python mcp_server.py
```

Check server status:
```bash
curl http://localhost:8000
```

### CORS Issues

The MCP server has CORS enabled for all origins. If you face issues, check:
- Server is running
- Correct API URL in environment.ts
- Network tab in browser DevTools

## 📦 Build for Production

```bash
# Create optimized build
npm run build

# Output will be in dist/finance-detective-app/
# Deploy to any static hosting service
```

### Deployment Options

- **Netlify**: Drag & drop `dist` folder
- **Vercel**: Connect GitHub repo
- **Firebase Hosting**: `firebase deploy`
- **GitHub Pages**: Use `angular-cli-ghpages`

## 🤝 Integration with Streamlit App

Both apps can run simultaneously:

1. **Streamlit App** (port 8501):
   ```bash
   streamlit run app.py
   ```

2. **MCP Server** (port 8000):
   ```bash
   python mcp_server.py
   ```

3. **Angular App** (port 4200):
   ```bash
   cd finance-detective-app
   npm start
   ```

## 🎨 Customization Ideas

1. **Add More Cases**: Edit `dashboard.component.ts`
2. **Custom Badges**: Modify badge system in `models.ts`
3. **New Themes**: Create theme variants in `styles.css`
4. **Animations**: Add more in component CSS files
5. **Sound Effects**: Add audio for achievements

## 📚 Learn More

- [Angular Documentation](https://angular.io/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [RxJS Guide](https://rxjs.dev/guide/overview)

## 🔮 Future Enhancements

- [ ] Real-time multiplayer competitions
- [ ] Leaderboards
- [ ] Daily challenges
- [ ] Social sharing
- [ ] Mobile app (Ionic)
- [ ] Voice narration for stories
- [ ] AR detective mode
- [ ] Mini-games between cases

## 📝 License

Part of the Financial Education project.

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review MCP server logs
3. Check browser console for errors

---

**Happy Investigating, Detective! 🕵️💰**
