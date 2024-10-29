import { MantineProvider } from '@mantine/core';
import Home from './pages/Home';
import '@mantine/core/styles.css';

function App() {
  return (
    <MantineProvider>
      <div className="App">
        <Home />
      </div>
    </MantineProvider>
  );
}

export default App;