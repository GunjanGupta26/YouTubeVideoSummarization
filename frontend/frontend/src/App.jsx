import axios from "axios";
import { useState } from "react";
import './App.css'
import React from 'react';
import Logo from './images/Logo.png'; 

function App() {
  const [disabled, setDisabled] = useState(true);
  const [inputValue, setInputValue] = useState("");
  const [response, setResponse] = useState("");
  const handleInputChange = (event) => {
    setInputValue(event.target.value);
    if (event.target.length === 0) {
      setDisabled(true);
    } else {
      setDisabled(false);
    }
  };

  const handleClick = async () => {
    axios
      .post("http://127.0.0.1:8000", {
        yt_link: inputValue,
      })
      .then((res) => {
        setResponse(res.data)
        console.log(res.data)
      });
    setInputValue("");
  };
  return (
    <div>
      <div className="left">
      <img  className="logo" src={Logo}style={{ width: '10%', marginTop: '2%' , marginLeft:'2%'}} alt="Logo" />
      </div>
      
      <div className="right">
      <h1>Youtube Video Summarizer</h1>
      <h2>Navigate YouTube with Ease: Concise Video Summaries</h2>
      </div>
      
      <p className="intro-text">Paste the youtube link below</p>
      <input
        type="text"
        value={inputValue}
        onChange={(event) => handleInputChange(event)}
      />
      <button onClick={handleClick} disabled={disabled} type="submit">
        Click
      </button>

      <div className="response">
      <p>Summary :</p>
      <p>{response}</p>
      </div>
      
    </div>
  );
}

export default App;
