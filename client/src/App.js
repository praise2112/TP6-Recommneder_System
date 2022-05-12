import './App.css';
import {Nav} from "./components/Nav";
import Search from "./components/Search";
import { ThemeProvider, createTheme } from '@mui/material/styles';
import {Box} from "@mui/material";
import {useRecommenderSystem} from "./hooks/useRecommenderSystem";
import Results from "./components/Results";

const darkTheme = createTheme({
    palette: {
        mode: 'dark',
    },
});

function App() {
    const recommender = useRecommenderSystem()
    return (
      <ThemeProvider theme={darkTheme}>
          <Box className="App" sx={{bgcolor: "background.default", width: "100%", height: '100%'}}>
              <Nav/>
              <div>
                <Search {...recommender}/>
                  <Results  {...recommender}/>
              </div>
        </Box>
      </ThemeProvider>
  );
}

export default App;
