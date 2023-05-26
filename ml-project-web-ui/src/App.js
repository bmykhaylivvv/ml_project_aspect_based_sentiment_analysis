import React, { useState, useRef } from "react";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import LoadingButton from "@mui/lab/LoadingButton";
import { CSSTransition } from "react-transition-group";

import ProgressBar from "./components/ProgressBar";
import Aspect from "./components/Aspect";

import styles from "./App.module.css";

const initialBackgroundColor = "#ece8f8";
const gradientColors = [
  "#fc0300",
  "#fa0501",
  "#f70801",
  "#f50a02",
  "#f20d02",
  "#f00f02",
  "#ed1203",
  "#eb1403",
  "#e81704",
  "#e61904",
  "#e31c04",
  "#e11e05",
  "#de2105",
  "#dc2306",
  "#d92606",
  "#d72806",
  "#d42b07",
  "#d22d07",
  "#cf3008",
  "#cd3208",
  "#ca3509",
  "#c73809",
  "#c53a09",
  "#c23d0a",
  "#c03f0a",
  "#bd420b",
  "#bb440b",
  "#b8470b",
  "#b6490c",
  "#b34c0c",
  "#b14e0d",
  "#ae510d",
  "#ac530d",
  "#a9560e",
  "#a7580e",
  "#a45b0f",
  "#a25d0f",
  "#9f600f",
  "#9d6210",
  "#9a6510",
  "#976811",
  "#956a11",
  "#926d11",
  "#906f12",
  "#8d7212",
  "#8b7413",
  "#887713",
  "#867913",
  "#837c14",
  "#817e14",
  "#7e8115",
  "#7c8315",
  "#798616",
  "#778816",
  "#748b16",
  "#728d17",
  "#6f9017",
  "#6d9218",
  "#6a9518",
  "#689718",
  "#659a19",
  "#629d19",
  "#609f1a",
  "#5da21a",
  "#5ba41a",
  "#58a71b",
  "#56a91b",
  "#53ac1c",
  "#51ae1c",
  "#4eb11c",
  "#4cb31d",
  "#49b61d",
  "#47b81e",
  "#44bb1e",
  "#42bd1e",
  "#3fc01f",
  "#3dc21f",
  "#3ac520",
  "#38c720",
  "#35ca20",
  "#32cd21",
  "#30cf21",
  "#2dd222",
  "#2bd422",
  "#28d723",
  "#26d923",
  "#23dc23",
  "#21de24",
  "#1ee124",
  "#1ce325",
  "#19e625",
  "#17e825",
  "#14eb26",
  "#12ed26",
  "#0ff027",
  "#0df227",
  "#0af527",
  "#08f728",
  "#05fa28",
  "#03fc29",
];

export default function App() {
  const [bgColor, setBgColor] = useState(initialBackgroundColor);
  const [userText, setUserText] = useState("");
  const [aspectsChecked, setAspectsChecked] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isPercentageBarVisible, setIsPercentageBarVisible] = useState(false);
  const [isAspectsVisible, setIsAspectsVisible] = useState(false);
  const [percentageBarScore, setPercentageBarScore] = useState(0);
  const [aspects, setAspects] = useState([]);
  const percentageBarRef = useRef(null);
  const aspectsContainerRef = useRef(null);

  async function proceedSentimentAnalysis(text) {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    };
    const res = await fetch("http://127.0.0.1:5000/sentiment", requestOptions);
    const parsedRes = await res.json();

    return parsedRes;
  }

  async function proceedAspects(text) {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    };
    const res = await fetch("http://127.0.0.1:5000/aspect", requestOptions);
    const parsedRes = await res.json();

    return parsedRes;
  }

  async function analyzeButtonClickHandler() {
    setAspects([])
    setIsAspectsVisible(false);
    setIsPercentageBarVisible(false);
    setIsLoading(true);

    const { result: sentimentScore } = await proceedSentimentAnalysis(userText);

    setIsLoading(false);

    const percentageSentimentScore = Math.floor(sentimentScore * 100);

    setPercentageBarScore(percentageSentimentScore);
    setBgColor(gradientColors[percentageSentimentScore - 1]);
    setIsPercentageBarVisible(true);

    if (aspectsChecked) {
      setIsAspectsVisible(false);
      setIsLoading(true);

      const { result: extractedAspects } = await proceedAspects(userText);

      setAspects(extractedAspects);
      setIsLoading(false);
      setIsAspectsVisible(true);
    }
  }

  const handleAspectToggleClick = (event) => {
    setAspectsChecked(event.target.checked);
  };

  return (
    <div
      className={styles.app}
      style={{
        backgroundColor: bgColor,
      }}
    >
      <div className={styles.contentContainer}>
        <div className={styles.header}>
          <div className={styles.title}>
            Harmonizing Reviews through Analysis
          </div>
          <div className={styles.subtitle}>
            Machine Learning UCU Course project
          </div>
        </div>

        <div className={styles.actionsContainer}>
          <TextField
            id="outlined-basic"
            multiline
            label="Your text"
            variant="outlined"
            className={styles.textInput}
            value={userText}
            onChange={(e) => setUserText(e.target.value)}
          />
          <FormControlLabel
            control={
              <Switch
                defaultChecked
                checked={aspectsChecked}
                onClick={handleAspectToggleClick}
              />
            }
            label="Include aspects"
          />
          <LoadingButton
            loading={isLoading}
            disabled={isLoading}
            variant="contained"
            size="large"
            onClick={analyzeButtonClickHandler}
          >
            Analyze
          </LoadingButton>

          <CSSTransition
            nodeRef={percentageBarRef}
            in={isPercentageBarVisible}
            timeout={500}
            classNames="my-default-transition"
          >
            <>
              {isPercentageBarVisible ? (
                <div
                  ref={percentageBarRef}
                  className={styles.percentageBarContainer}
                  key="percentageBarContainer"
                >
                  <ProgressBar
                    bgcolor={bgColor}
                    completed={percentageBarScore}
                  />
                </div>
              ) : null}
            </>
          </CSSTransition>

          <CSSTransition
            nodeRef={aspectsContainerRef}
            in={isAspectsVisible}
            timeout={500}
            classNames="my-default-transition"
          >
            <>
              {isAspectsVisible ? (
                <div
                  ref={aspectsContainerRef}
                  className={styles.aspectsContainer}
                >
                  {aspects.map((aspect, i) => (
                    <Aspect
                      key={i}
                      name={aspect.name}
                      descriptions={aspect.descriptions}
                    />
                  ))}
                </div>
              ) : null}
            </>
          </CSSTransition>
        </div>
      </div>
    </div>
  );
}
