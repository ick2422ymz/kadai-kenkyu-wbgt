<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WBGT値計算</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* LEDインジケーターの色と光彩エフェクトの定義 */
        .led-red { background-color: #ef4444; }
        .led-red.active { box-shadow: 0 0 40px 15px rgba(239, 68, 68, 0.8); opacity: 1; }
        .led-red.inactive { opacity: 0.15; }

        .led-yellow { background-color: #eab308; }
        .led-yellow.active { box-shadow: 0 0 40px 15px rgba(234, 179, 8, 0.8); opacity: 1; }
        .led-yellow.inactive { opacity: 0.15; }

        .led-green { background-color: #22c55e; }
        .led-green.active { box-shadow: 0 0 40px 15px rgba(34, 197, 94, 0.8); opacity: 1; }
        .led-green.inactive { opacity: 0.15; }
    </style>
</head>
<body class="bg-gray-200 h-screen w-screen p-4 m-0 box-border overflow-hidden">

    <!-- 画面を縦に3分割するコンテナ -->
    <div class="flex flex-col md:flex-row h-full w-full gap-4">
        
        <!-- ==============================
             1. データ入力画面（左側）
        =============================== -->
        <div class="flex-1 bg-white rounded-2xl shadow-xl p-8 flex flex-col justify-center relative">
            <div class="absolute top-8 left-0 w-full text-center">
                <h2 class="text-2xl font-bold text-gray-800">データ入力</h2>
                <p class="text-sm text-gray-500 mt-1">数値を入力すると自動で計算されます</p>
            </div>
            
            <div class="w-full max-w-sm mx-auto space-y-8 input-area-container">
                <div>
                    <label for="temperature" class="block text-gray-700 font-bold mb-3 text-lg">温度 [℃]</label>
                    <input type="number" id="temperature" step="0.1" class="shadow-inner border-2 border-gray-300 rounded-xl w-full py-4 px-5 text-gray-700 text-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition" placeholder="例: 23.2">
                </div>
                
                <div>
                    <label for="humidity" class="block text-gray-700 font-bold mb-3 text-lg">湿度 [%]</label>
                    <!-- 湿度は整数のみ入力可能（step="1"）に変更 -->
                    <input type="number" id="humidity" step="1" class="shadow-inner border-2 border-gray-300 rounded-xl w-full py-4 px-5 text-gray-700 text-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition" placeholder="例: 44">
                </div>
            </div>
        </div>

        <!-- ==============================
             2. WBGT計算値表示画面（中央）
        =============================== -->
        <div class="flex-1 bg-white rounded-2xl shadow-xl p-8 flex flex-col justify-center items-center relative">
            <div class="absolute top-8 w-full text-center">
                <h2 class="text-2xl font-bold text-gray-800">室内WBGT目安</h2>
            </div>

            <div id="wbgt-box" class="w-full p-8 rounded-2xl border-4 flex flex-col justify-center items-center transition-colors duration-300 bg-gray-50 border-gray-200">
                <div class="flex items-baseline justify-center flex-wrap gap-2 text-gray-700" id="wbgt-text-color">
                    <span class="text-3xl font-bold">WBGT</span>
                    <span id="result-wbgt" class="text-7xl lg:text-8xl font-extrabold tracking-tighter">--.-</span>
                    <span class="text-3xl font-bold">［℃］</span>
                </div>
            </div>
            <p id="status-text" class="mt-8 text-center font-bold text-2xl text-gray-400">データ待機中...</p>
        </div>

        <!-- ==============================
             3. LED表示画面（右側）
        =============================== -->
        <div class="flex-1 bg-white rounded-2xl shadow-xl p-8 flex flex-col justify-center items-center relative">
            <div class="absolute top-8 w-full text-center">
                <h2 class="text-2xl font-bold text-gray-800">ステータス</h2>
            </div>

            <!-- 信号機風のLEDコンテナ -->
            <div class="bg-gray-800 p-8 rounded-[50px] flex flex-col gap-8 shadow-inner border-4 border-gray-900">
                <div id="led-red" class="w-24 h-24 rounded-full led-red inactive transition-all duration-300"></div>
                <div id="led-yellow" class="w-24 h-24 rounded-full led-yellow inactive transition-all duration-300"></div>
                <div id="led-green" class="w-24 h-24 rounded-full led-green inactive transition-all duration-300"></div>
            </div>
        </div>

    </div>

    <!-- メインの計算プログラム -->
    <script>
        function calculateAndUpdate() {
            const T = parseFloat(document.getElementById('temperature').value);
            // 湿度は整数としてパース（念のためMath.roundで丸める）
            const RH_raw = parseFloat(document.getElementById('humidity').value);
            const RH = isNaN(RH_raw) ? NaN : Math.round(RH_raw);
            
            const ledRed = document.getElementById('led-red');
            const ledYellow = document.getElementById('led-yellow');
            const ledGreen = document.getElementById('led-green');
            const wbgtBox = document.getElementById('wbgt-box');
            const statusText = document.getElementById('status-text');
            const resultWbgt = document.getElementById('result-wbgt');
            const textColor = document.getElementById('wbgt-text-color');

            ledRed.className = 'w-24 h-24 rounded-full led-red inactive transition-all duration-300';
            ledYellow.className = 'w-24 h-24 rounded-full led-yellow inactive transition-all duration-300';
            ledGreen.className = 'w-24 h-24 rounded-full led-green inactive transition-all duration-300';

            if (isNaN(T) || isNaN(RH)) {
                resultWbgt.innerText = '--.-';
                wbgtBox.className = 'w-full p-8 rounded-2xl border-4 flex flex-col justify-center items-center transition-colors duration-300 bg-gray-50 border-gray-200';
                textColor.className = 'flex items-baseline justify-center flex-wrap gap-2 text-gray-400';
                statusText.innerText = "データ待機中...";
                statusText.className = "mt-8 text-center font-bold text-2xl text-gray-400";
                return;
            }

            const term1 = T * Math.atan(0.151977 * Math.pow(RH + 8.313659, 0.5));
            const term2 = Math.atan(T + RH);
            const term3 = - Math.atan(RH - 1.676331);
            const term4 = 0.00391838 * Math.pow(RH, 1.5) * Math.atan(0.023101 * RH);
            const term5 = - 4.686035;
            const Tw = term1 + term2 + term3 + term4 + term5;

            const WBGT = 0.7 * Tw + 0.3 * T;
            const finalWBGT = Math.floor(WBGT * 10 + 0.5) / 10;

            resultWbgt.innerText = finalWBGT.toFixed(1);

            if (finalWBGT < 21) {
                ledGreen.classList.replace('inactive', 'active');
                wbgtBox.className = 'w-full p-8 rounded-2xl border-4 flex flex-col justify-center items-center transition-colors duration-300 bg-green-50 border-green-200';
                textColor.className = 'flex items-baseline justify-center flex-wrap gap-2 text-green-700';
                statusText.innerText = "安全";
                statusText.className = "mt-8 text-center font-bold text-2xl text-green-600";
            } else if (finalWBGT < 28) {
                ledYellow.classList.replace('inactive', 'active');
                wbgtBox.className = 'w-full p-8 rounded-2xl border-4 flex flex-col justify-center items-center transition-colors duration-300 bg-yellow-50 border-yellow-200';
                textColor.className = 'flex items-baseline justify-center flex-wrap gap-2 text-yellow-700';
                statusText.innerText = "注意";
                statusText.className = "mt-8 text-center font-bold text-2xl text-yellow-600";
            } else {
                ledRed.classList.replace('inactive', 'active');
                wbgtBox.className = 'w-full p-8 rounded-2xl border-4 flex flex-col justify-center items-center transition-colors duration-300 bg-red-50 border-red-200';
                textColor.className = 'flex items-baseline justify-center flex-wrap gap-2 text-red-700';
                statusText.innerText = "厳重注意";
                statusText.className = "mt-8 text-center font-bold text-2xl text-red-600";
            }
        }

        setInterval(calculateAndUpdate, 1000);
        calculateAndUpdate();
    </script>


    <!-- =======================================================================================
         ↓↓↓【テスト用・削除対象】↓↓↓
         以下のスクリプトは、センサ完成までのテスト用「ダミーデータ発生コード」です。
         本番環境でセンサデータを取得する際は、このコメントブロックから下をすべて削除してください。
    ======================================================================================== -->
    <script>
        (function() {
            // 1. スイッチUIの追加
            const switchContainer = document.createElement('div');
            switchContainer.className = 'mt-10 p-5 bg-gray-50 border-2 border-dashed border-gray-400 rounded-2xl flex flex-col items-center justify-center';
            switchContainer.innerHTML = `
                <span class="text-sm text-gray-500 mb-4 font-bold tracking-wider">※テスト用ダミーセンサ</span>
                <label class="flex items-center cursor-pointer">
                    <div class="relative">
                        <input type="checkbox" id="dummy-switch" class="sr-only">
                        <div id="switch-bg" class="block bg-gray-400 w-16 h-8 rounded-full transition-colors duration-300 shadow-inner"></div>
                        <div id="switch-dot" class="absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform duration-300 shadow-md"></div>
                    </div>
                    <div class="ml-4 text-gray-800 font-bold text-xl">
                        ダミー発生 <span id="switch-status-text" class="text-gray-400 ml-1">OFF</span>
                    </div>
                </label>
            `;
            
            // データ入力エリアのコンテナを取得して末尾に追加
            const inputArea = document.querySelector('.input-area-container');
            if(inputArea) inputArea.appendChild(switchContainer);

            // 2. ダミーデータ発生のロジック
            let dummyInterval = null;
            let currentTemp = 25.0; // 初期値（温度は小数点第1位あり）
            let currentHum = 50;    // 初期値（湿度は整数のみ）

            function generateDummyData() {
                // 少しずつ変動させるための計算
                // 温度は±0.5度
                let deltaT = (Math.random() - 0.5) * 1.0; 
                // 湿度は±3%の範囲で整数値で動かす
                let deltaHum = Math.round((Math.random() - 0.5) * 6.0);

                currentTemp += deltaT;
                currentHum += deltaHum;

                // 境界条件の処理 (温度 5.0 ~ 35.0 / 湿度 20 ~ 90) 端に行ったら反発させる
                if (currentTemp < 5.0)  { currentTemp = 5.0 + Math.abs(deltaT); }
                if (currentTemp > 35.0) { currentTemp = 35.0 - Math.abs(deltaT); }
                if (currentHum < 20)  { currentHum = 20 + Math.abs(deltaHum); }
                if (currentHum > 90)  { currentHum = 90 - Math.abs(deltaHum); }

                // 入力欄に値をセット (湿度は小数点なしの整数表示)
                document.getElementById('temperature').value = currentTemp.toFixed(1);
                document.getElementById('humidity').value = Math.round(currentHum);
            }

            // 3. スイッチのON/OFFイベント
            const dummySwitch = document.getElementById('dummy-switch');
            dummySwitch.addEventListener('change', (e) => {
                const isChecked = e.target.checked;
                const tInput = document.getElementById('temperature');
                const hInput = document.getElementById('humidity');
                const bg = document.getElementById('switch-bg');
                const dot = document.getElementById('switch-dot');
                const statusText = document.getElementById('switch-status-text');

                if (isChecked) {
                    // スイッチON時のUI変化
                    bg.classList.replace('bg-gray-400', 'bg-blue-500');
                    dot.classList.add('translate-x-8');
                    statusText.innerText = "ON";
                    statusText.className = "text-blue-600 ml-1";

                    // 入力欄をロック（入力不可・グレーアウト）
                    tInput.disabled = true;
                    hInput.disabled = true;
                    tInput.classList.add('bg-gray-200', 'cursor-not-allowed', 'text-gray-400');
                    hInput.classList.add('bg-gray-200', 'cursor-not-allowed', 'text-gray-400');

                    // 現在の入力欄に値があればそれをスタート地点にする
                    if (tInput.value) currentTemp = parseFloat(tInput.value);
                    if (hInput.value) currentHum = Math.round(parseFloat(hInput.value));

                    // 直ちに1回データ発生させ、その後1秒周期(1000ms)で実行
                    generateDummyData();
                    dummyInterval = setInterval(generateDummyData, 1000);
                } else {
                    // スイッチOFF時のUI変化
                    bg.classList.replace('bg-blue-500', 'bg-gray-400');
                    dot.classList.remove('translate-x-8');
                    statusText.innerText = "OFF";
                    statusText.className = "text-gray-400 ml-1";

                    // 入力欄のロック解除
                    tInput.disabled = false;
                    hInput.disabled = false;
                    tInput.classList.remove('bg-gray-200', 'cursor-not-allowed', 'text-gray-400');
                    hInput.classList.remove('bg-gray-200', 'cursor-not-allowed', 'text-gray-400');

                    // ダミーデータの発生を停止
                    clearInterval(dummyInterval);
                }
            });
        })();
    </script>
</body>
</html>
