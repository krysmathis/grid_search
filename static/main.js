var myCanvas = document.getElementById('myCanvas');

coords = []

// const uploadForm = document.querySelector('.form__upload')
// uploadForm.onsubmit = (event) => {
//     event.preventDefault();
//     openFile(event)
// }


// drawCoordinates(46,12)
// drawCoordinates(546,20)
// drawCoordinates(501,731)
// drawCoordinates(80,718)

function addCoord (coord)  {
    
    coords.push(coord)
    publishCoords()
}

const submit = () => {

    const xs = coords.map(c => c['x'])
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)

    const ys = coords.map(c => c['y'])
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)    


    // extract file name from img.src
    var url = img.src
    var filename = url.substring(url.lastIndexOf('/')+1);

    const pogEl = document.querySelector("#select__pog")
    const pog = pogEl[pogEl.selectedIndex].text
    
    const upload = {
        'bbox': [minY,maxY,minX,maxX],
        'coords': coords,
        'image': img_bucket + filename,
        'pog': pog
    }

    window.fetch('/upload', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(upload),
    }).then(result => {

        return result.json()

    }).then(data => {

        publishImages(data)
        document.getElementById('img__results').src = './static/images/tide_whatever.jpg'
    });
}

var publishImages = (data) => {

    const results = document.getElementById('img__slices')

    const missing_items = data.reduce((m,v)=>{
        if (v.is_light === 0){
            m.push(v)
        }
        return m
    },[])

    const missingEl = document.getElementById('missing-items')
    let html = '<div class="outs">OUTS</div>'
    
    missing_items.forEach(m => {
        var url = m.path
        var filename = url.substring(url.lastIndexOf('/')+1);
        html = html + '<div class="outs__item">' + filename + '</div>'
    })
    
    missingEl.innerHTML = html

    data.forEach(d => {

        var div = document.createElement('div')
        var DOM_img = document.createElement("img");
        DOM_img.src = d.path

        var url = DOM_img.src
        var filename = url.substring(url.lastIndexOf('/')+1);
        DOM_img.title = filename;

        div.innerHTML = '<div>' + filename + ' ' + d.is_light + '</div>';
        div.appendChild(DOM_img);
        results.appendChild(div);

    });
};

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
        //console.log('dataURL', dataURL)
       // var output = document.getElementById('mainImage');
        img.src = dataURL;
        
        canvasImg = myCanvas.toDataURL('')
        setTimeout(function(){
            var c = document.getElementById("myCanvas");
            var ctx = c.getContext("2d");   
            ctx.drawImage(img, 0, 0)
        }, 500);


    };
    reader.readAsDataURL(input.files[0]);
    //console.log(input.files[0])
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

function populatePogSelector() {
    fetch("./static/planograms.json")
    .then(res => res.json())
    .then(data => {

        const pogs = data.reduce((m,v) => {
            m.push(v['planogram'])
            return m
        },[])

        const dataTypes = pogs
        const inputEl = document.querySelector("#select__pog")
            dataTypes.map((d,i) => {
                inputEl.options[inputEl.options.length] = new Option(d,`${i}`);
            })
    })
}
populatePogSelector()