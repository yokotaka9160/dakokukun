 function clock(){

  // 数字が 1ケタのとき、「0」を加えて 2ケタにする
  var twoDigit =function(num){
    　     var digit
         if( num < 10 )
          { digit = "0" + num; }
         else { digit = num; }
         return digit;
   }
  // 曜日を表す各文字列の配列
  var weeks = new Array("日","月","火","水","木","金","土");

 // 現在日時を表すインスタンスを取得
  var now = new Date();

    var year = now.getFullYear();
    var month = twoDigit(now.getMonth() + 1)
    var day = twoDigit(now.getDate());
    var week = weeks[now.getDay()];
    var hour = twoDigit(now.getHours());
    var minute = twoDigit(now.getMinutes());
    var second = twoDigit(now.getSeconds());
 //　HTML: <div id="clock_date">(ココの日付文字列を書き換え)</div>
document.getElementById("clock_date").textContent =  year + "/" + month + "/" + day + " (" + week + ")";
// console.log(document.getElementById("date").value);
document.getElementById("date").value =  year + "/" + month + "/" + day;
document.getElementById("datetime").value =  year + "/" + month + "/" + day + " " + hour + ":" + minute + ":" + second;

//　HTML: <div id="clock_time">(ココの時刻文字列を書き換え)</div>
document.getElementById("clock_time").textContent = hour + ":" + minute + ":" + second;
document.getElementById("time").value = hour + ":" + minute + ":" + second;
document.getElementById("day").value = day;
document.getElementById("DayOfTheWeek").value = week;


}
// 上記のclock関数を1000ミリ秒ごと(毎秒)に実行
setInterval(clock, 1000);



