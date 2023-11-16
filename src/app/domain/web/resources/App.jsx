import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import "./App.css";

function App() {
  const [count, setCount] = useState(0);

  return (
    <h1 className="text-3xl font-bold text-red-500 underline text-center">
      Hello world!
    </h1>
  );
}

export default App;
