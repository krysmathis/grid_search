var imageFile = "";    

var openFile = function(event) {
    var input = event.target;
    var reader = new FileReader();
    reader.onload = function(){
        var dataURL = reader.result;
        var output = document.getElementById('mainImage');
        output.src = dataURL;
        setTimeout(function(){
            anno.reset();
        }, 100);
    };
    imageFile = input.files[0];
    reader.readAsDataURL(input.files[0]);
};

// prints 
function showBoxes(){
    var myNode = document.getElementById("myList");
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
        
    var annoList = anno.getAnnotations();
    //if (annoList.length == 0) return;
    // copy object (for safety)
    annoList = JSON.parse(JSON.stringify(annoList));

    var width = document.getElementById("mainImage").width; 
    var height = document.getElementById("mainImage").height; 
    // make all annotations have pixel coordinates
    for (var ind = 0; ind < annoList.length; ind++){
        var curAnno = annoList[ind];
        var curGeom = curAnno.shapes[0].geometry;
        // means not using pixel coordinates
        if (curGeom.height < 1 || curGeom.width < 1){
            curGeom.height = Math.round(curGeom.height * height);
            curGeom.width = Math.round(curGeom.width * width);
            curGeom.x = Math.round(curGeom.x * width);
            curGeom.y = Math.round(curGeom.y * height);
        }
        var xminStr = String(curGeom.x);
        var xmaxStr = String(curGeom.x + curGeom.width);
        var yminStr = String(curGeom.y);
        var ymaxStr = String(curGeom.y + curGeom.height);
        var textStr = curAnno.text;
        //console.log(curAnno);
        //console.log(curGeom);
        curAnno.shapes[0].units = "pixels";
        var node = document.createElement("CODE");
        var brNode = document.createElement("BR");
        var textnode = document.createTextNode(textStr + " " + xminStr + " " + yminStr + " " + xmaxStr + " " + ymaxStr);
        node.appendChild(textnode);
        document.getElementById("myList").appendChild(node);
        document.getElementById("myList").appendChild(brNode);
    }

}


var generateAnnotatedImage = function() {
    var annoList = anno.getAnnotations();
    //if (annoList.length == 0) return;
    // copy object (for safety)
    annoList = JSON.parse(JSON.stringify(annoList));
    var width = document.getElementById("mainImage").width; 
    var height = document.getElementById("mainImage").height; 
    // make all annotations have pixel coordinates
    var image = {};


    for (var ind = 0; ind < annoList.length; ind++){
        var curAnno = annoList[ind];
        var curGeom = curAnno.shapes[0].geometry;
        // means not using pixel coordinates
        if (curGeom.height < 1 || curGeom.width < 1){
            curGeom.height = Math.round(curGeom.height * height);
            curGeom.width = Math.round(curGeom.width * width);
            curGeom.x = Math.round(curGeom.x * width);
            curGeom.y = Math.round(curGeom.y * height);
        }
        var xminStr = String(curGeom.x);
        var xmaxStr = String(curGeom.x + curGeom.width);
        var yminStr = String(curGeom.y);
        var ymaxStr = String(curGeom.y + curGeom.height);
        var textStr = curAnno.text;
        dict = {}
        image[textStr] = [xminStr, yminStr,xmaxStr,ymaxStr];
    }
    return image;
}


// prints 
function showBoxes(){
    var width = document.getElementById("mainImage").width; 
    var height = document.getElementById("mainImage").height; 

    var myNode = document.getElementById("myList");
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
        var images = generateAnnotatedImage();   
        const results = {}
        results['planogram'] = "test"
        results['items'] = images
        results['width'] = width
        results['height'] = height
        var node = document.createElement("PRE");
        var textNode = document.createTextNode(JSON.stringify(results, null, '  '));
        node.appendChild(textNode);
        document.getElementById("myList").appendChild(node);
    
}