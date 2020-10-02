var loadContent = function(event) {
    var image = document.getElementById('content_image');
    image.src = URL.createObjectURL(event.target.files[0]);
    };
var loadStyle = function(event) {
    var image = document.getElementById('style_image');
    image.src = URL.createObjectURL(event.target.files[0]);
    };
    

//sending images to API
img1 = document.getElementById("img1");
img2 = document.getElementById("img2");
myForm = document.getElementById("myForm");
myForm.addEventListener("submit",async e =>{
    e.preventDefault();
    formData = new FormData();
    formData.append("img1",img1.files[0]);
    formData.append("img2",img2.files[0]);

    const names = ["we are processing your request.","Please wait for some moments..","Its almost Completed.."]
    var i= 0
    setInterval(function() {
    // var rand = Math.floor(Math.random() * 4);
    document.getElementById("txt").innerHTML = names[i];
    i=i+1;
    if(i==3){
        i=0;
    }
    }, 10000);

    fetch("/style",{method:"post", body: formData}).then(
        response => response.blob()
    ).then(
        data => {
            //image rescieved displayed on page
            document.getElementById("txt").style.display="none";
            document.getElementById('result').style.display ="block";
            document.getElementById('result').src = URL.createObjectURL(data);
        }
    );

});