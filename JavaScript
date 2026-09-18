```javascript:script.js
// 1. HTML内にある各部品（要素）を探して、JavaScriptから操作できるように変数に格納します
const tempSlider = document.getElementById('temp-slider');
const humSlider = document.getElementById('hum-slider');
const tempDisplay = document.getElementById('temp-display');
const humDisplay = document.getElementById('hum-display');
const wbgtDisplay = document.getElementById('wbgt-display');
const statusText = document.getElementById('status-text');

const ledGreen = document.getElementById('led-green');
const ledYellow = document.getElementById('led-yellow');
const ledRed = document.getElementById('led-red');

// 2. WBGTを計算する関数（Arduinoで実装したC++の計算式と同じです）
function calculateWBGT(T, RH) {
    const term1 = T * Math.atan(0.151977 * Math.pow(RH + 8.313659, 0.5));
    const term2 = Math.atan(T + RH);
    const term3 = - Math.atan(RH - 1.676331);
    const term4 = 0.00391838 * Math.pow(RH, 1.5) * Math.atan(0.023101 * RH);
    const term5 = - 4.686035;
    
    const Tw = term1 + term2 + term3 + term4 + term5;
    const WBGT = 0.7 * Tw + 0.3 * T;
    
    // 小数点第1位で四捨五入して返します
    return Math.round(WBGT * 10) / 10;
}

// 3. スライダーが動かされたときに実行されるメインプログラム
function updateSimulator() {
    // スライダーの現在の値を取得（Tinkercadの analogRead の代わり）
    const T = parseFloat(tempSlider.value);
    const RH = parseFloat(humSlider.value);

    // 画面の数値表示を更新
    tempDisplay.innerText = T.toFixed(1);
    humDisplay.innerText = RH;

    // WBGTを計算
    const wbgt = calculateWBGT(T, RH);

    // 計算結果をディスプレイに表示
    wbgtDisplay.innerText = wbgt.toFixed(1);

    // LEDの状態をリセット（全てから 'on' クラスを外す = 消灯）
    ledGreen.classList.remove('on');
    ledYellow.classList.remove('on');
    ledRed.classList.remove('on');

    // ArduinoのIf構文と同じロジックで判定し、LEDを点灯（'on' クラスを追加）
    if (wbgt < 21.0) {
        // 安全
        ledGreen.classList.add('on');
        statusText.innerText = "SAFE (安全)";
        statusText.style.color = "#2ecc71";
        wbgtDisplay.style.color = "#2ecc71";
    } else if (wbgt < 28.0) {
        // 注意
        ledYellow.classList.add('on');
        statusText.innerText = "CAUTION (注意)";
        statusText.style.color = "#f1c40f";
        wbgtDisplay.style.color = "#f1c40f";
    } else {
        // 警戒
        ledRed.classList.add('on');
        statusText.innerText = "WARNING (警戒)";
        statusText.style.color = "#e74c3c";
        wbgtDisplay.style.color = "#e74c3c";
    }
}

// 4. スライダーが動かされるたびに updateSimulator 関数を自動的に実行するよう設定
tempSlider.addEventListener('input', updateSimulator);
humSlider.addEventListener('input', updateSimulator);

// 5. ページを読み込んだ直後にも1回実行し、初期状態をセットする
updateSimulator();
```eof

**【JavaScriptの解説】**
*   `calculateWBGT`: Arduino（C++）やPythonで作成した数式と全く同じロジックをJavaScriptの記述（`Math.pow` など）に翻訳したものです。
*   `ledGreen.classList.add('on')`: これがArduinoの `digitalWrite(greenPin, HIGH)` に相当します。HTMLの要素に `on` というクラスを付けることで、CSSで設定した「光るエフェクト」が適用されます。逆に `classList.remove('on')` で消灯（LOW）します。
