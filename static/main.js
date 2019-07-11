var myCanvas = document.getElementById('myCanvas');
console.log(myCanvas)

coords = []

function addCoord (coord)  {
    
    coords.push(coord)
    publishCoords()
}

const submit = () => {

    const xs = coords.map(c => c['x'])
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    console.log(minX, maxX,coords)

    const ys = coords.map(c => c['y'])
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)    
    console.log(minY, maxY)

    // extract file name from img.src
    var url = img.src
    var filename = url.substring(url.lastIndexOf('/')+1);

    const upload = {
        'bbox': [minY,maxY,minX,maxX],
        'coords': coords,
        'image': './static/images/' + filename
    }

    console.log(upload)
    window.fetch('/upload', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(upload),
    }).then(result => {

        return result.json()

    }).then(data => {
        console.log(data)
        publishImages(data)
        document.getElementById('img__results').src = './static/images/tide_whatever.jpg'
    });
}

var publishImages = (data) => {
    const results = document.getElementById('img__slices')
    
    data.forEach(d => {
        var DOM_img = document.createElement("img");
        DOM_img.src = d;
    
        results.appendChild(DOM_img);
    })

}

const publishCoords = () => {
    str = ''
    coords.forEach(c => {
        str = str + c.x  + ':' + c.y + ','
    })
    document.getElementById('coords').innerHTML = str

}

var openFile = function(event) {
    var input = event.target;
    var reader = new FileReader();
    reader.onload = function(){
        var dataURL = reader.result;
       // var output = document.getElementById('mainImage');
        img.src = dataURL;
        
        
        setTimeout(function(){
            var c = document.getElementById("myCanvas");
            var ctx = c.getContext("2d");   
            ctx.drawImage(img, 0, 0);
        }, 100);
    };
    reader.readAsDataURL(input.files[0]);
};


// var img = new Image()
// img.src = "./static/images/tide.jpg";

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
        
     if (coords.length == 4) {
        var c = document.getElementById("myCanvas");
        var ctx = c.getContext("2d");
        
        ctx.drawImage(img, 0, 0);
        coords = []
    }


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