
function check(val) {
    //alert(document.ansform.ans.value);
    document.read.action=val;
    document.read.submit();
}
  

// document.addEventListener('DOMContentLoaded', function () {
//   function checkBreakPoint() {
//     var width = window.innerWidth;

//     if (width <= 780) {
//       $("#menu").detach();

//     } else {
//       // $("#hamburger-menu").remove();
//       // $('#menu').append();
//       $('#header').append();
//       $("#hamburger-menu").detach();
      
//     }
//   }

//   // リサイズの監視
//   window.addEventListener('resize', checkBreakPoint);

//   // 初回チェック
//   checkBreakPoint();
// });
document.addEventListener("DOMContentLoaded", function(){
const open = document.querySelector("#open");
const close = document.querySelector("#close");
const g_menu = document.querySelector("#g_menu");

//メニューを出す
open.addEventListener('click', function() {
    g_menu.classList.add('inside');
    g_menu.classList.remove('outside');
 }, false);

//メニューを隠す
close.addEventListener('click', function() {
    g_menu.classList.remove('inside');
    g_menu.classList.add('outside');
 }, false);
},false);