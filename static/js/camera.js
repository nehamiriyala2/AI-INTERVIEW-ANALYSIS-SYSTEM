// const video = document.getElementById("camera");

// if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
//     navigator.mediaDevices.getUserMedia({ video: true })
//         .then(function (stream) {
//             video.srcObject = stream;
//         })
//         .catch(function (error) {
//             alert("Camera access denied or not available");
//         });
// } else {
//     alert("Camera not supported in this browser");
// }




// navigator.mediaDevices.getUserMedia({ video: true })
//   .then(stream => {
//     document.getElementById("camera").srcObject = stream;
//   });



navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        document.getElementById("video").srcObject = stream;
    })
    .catch(err => {
        alert("Camera access denied");
    });