var myCanvas = document.getElementById('myCanvas');
console.log(myCanvas)

coords = []

function addCoord (coord)  {
    coords.push(coord)
    publishCoords()
}

const publishCoords = () => {
    str = ''
    coords.forEach(c => {
        str = str + c.x  + ':' + c.y + ','
    })
    document.getElementById('coords').innerHTML = str

    window.fetch('/coords', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(coords),
      }).then(result => {
        
            result.json()
        
      }).then(data => {
          console.log((data))
      });



}

var img = new Image()
img.src = "./static/tide.jpg";

img.onload = function() {
    // img.width = 200
    myCanvas.width = img.width 
    myCanvas.height = img.height 
}

window.onload = function() {
    var c = document.getElementById("myCanvas");
    var ctx = c.getContext("2d");
    
    ctx.drawImage(img, 0, 0);
  };

myCanvas.addEventListener('click', function(e) {
    getPosition(e)
}, false);


var pointSize = 10;

function getPosition(event){
     var rect = myCanvas.getBoundingClientRect();
     var x = event.clientX - rect.left;
     var y = event.clientY - rect.top;
        
     drawCoordinates(x,y);
     coord = {'x':x,'y':y}
     addCoord(coord);
}


function clearLastPoint() {
    
    var c = document.getElementById("myCanvas");
    var ctx = c.getContext("2d");
    
    ctx.drawImage(img, 0, 0);
    console.log(coords)
    const lastPoint = coords.pop()
    coords.forEach(c => {
        drawCoordinates(c.x,c.y)
    })
}

function drawCoordinates(x,y){	
  	var ctx = document.getElementById("myCanvas").getContext("2d");


  	ctx.fillStyle = "white"; // Red color

    ctx.beginPath();
    ctx.arc(x, y, pointSize, 0, Math.PI * 2, true);
    ctx.fill();
}