"use strict"
const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
const endpoint="dog-o-matic/api/v1/"
const socketio=io(`http://${lanIP}`);
const backend = "http://" + lanIP

const showSensorData = function(jsonData){

  console.log(jsonData);
  let html = ``;
  jsonData.data.forEach(element => {
    html += `<tr><td>${element.beschrijving}</td><td>${element.datum}</td><td>${element.value}</td><td>${element.eenheid}</td></tr>`
  });
  document.querySelector(".js-table").innerHTML += html;
};

const getSensorData = function(sensorid){

  handleData(backend + `/dog-o-matic/api/v1/data`, showSensorData);
};
const listentoHomeUI = function () {
  document.querySelector(".js-feed-button").addEventListener("click", function () {
    socketio.emit("F2B_schakelen")
  })
};

function myFunction() {
  var x = document.getElementById("myDIV");
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}

const init = function(){
  if(document.querySelector(".js-statistics")){
    getSensorData()
  }
  if(document.querySelector(".js-home")){
    listentoHomeUI();
    $.notify.defaults({"position":"right bottom"})
    $.notify("boe")
  }
  if(document.querySelector(".js-settings")){
    document.querySelector(".js-time").defaultValue = "17:30";
  }
  

};
document.addEventListener("DOMContentLoaded", init)

