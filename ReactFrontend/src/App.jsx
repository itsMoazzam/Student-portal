import { BrowserRouter as Router } from "react-router-dom";
import Rout from "./Rout";
import { AuthProvider } from "./context/AuthContext";
const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Rout />
      </Router>
    </AuthProvider>
  );
};

export default App;
