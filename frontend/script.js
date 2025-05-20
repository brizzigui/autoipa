let mediaRecorder;
let audioChunks = [];
let is_recording = false;
let stream;

async function toggle()
{
    if(is_recording)
    {
        is_recording = false;
        stop_recording();
    }

    else
    {
        is_recording = true;
        start_recording();
    }
}

async function start_recording()
{
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    audioChunks = [];
    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
    document.getElementById('button_background').style.display = "block";
    document.getElementById('button_img').src = '/frontend/assets/stop.svg';
}

async function stop_recording() {
    const tracks = stream.getTracks();
    tracks.forEach(track => {
        track.stop()
    })

    mediaRecorder.stop();
    mediaRecorder.onstop = async () => {
        document.getElementById('input').style.display = "none";
        document.getElementById('loading').style.display = "block";
        
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        write_results(data);
        
        document.getElementById('button_img').src = '/frontend/assets/recording.svg';
        document.getElementById('toggle').classList.remove("toggled");

        document.getElementById('loading').style.display = "none";
        document.getElementById('result_box').style.display = "block";

    };
}

function copy_to_clipboard(id)
{
    alert("Copied to clipboard.");
    let transcription = document.getElementById(id).innerText;
    navigator.clipboard.writeText(transcription.replaceAll(" ", ""));
}

async function upload_file()
{
    document.getElementById('input').style.display = "none";
    document.getElementById('loading').style.display = "block";
    
    let audio = document.getElementById("upload_field").files[0];
    const formData = new FormData();
    formData.append('audio', audio, 'recording.wav');
    
    const response = await fetch('/upload_file', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    write_results(data);

    document.getElementById('button_img').src = '/frontend/assets/recording.svg';
    document.getElementById('toggle').classList.remove("toggled");

    document.getElementById('loading').style.display = "none";
    document.getElementById('result_box').style.display = "block";
}

function write_results(data)
{
    document.getElementById('output').innerHTML = "<h3 class='results_title'>Transcriptions</h3>" + "<hr>" +
    "<p class='results_model_title'><img class='tiny_icon' src='/frontend/assets/bolt.svg'>Best model:</p>" + 
    "<p class='results_model_id'>wav2vec2_xlsr_53</p>" +
    '<h3 id="best_model">' + " / " + data.facebook_wav2vec2_xlsr_53_espeak_cv_ft + " /" + '</h3>' +
    "<img class='tiny_icon' style='margin: 5px 0px 10px 0px' src='/frontend/assets/copy.svg' onclick='copy_to_clipboard(`best_model`);'>" +
    "<hr>" + "<p class='results_model_title'><img class='tiny_icon' src='/frontend/assets/alt.svg'>Alternative model:</p> <p class='results_model_id'>wav2vec2_lv_60</p>" + 
    '<h3 id="alternative_model">' + " / " + data.facebook_wav2vec2_lv_60_espeak_cv_ft + " /"  + '</h3>' +
    "<img class='tiny_icon' style='margin: 5px' src='/frontend/assets/copy.svg' onclick='copy_to_clipboard(`alternative_model`);'>"
}