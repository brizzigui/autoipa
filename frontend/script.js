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
        document.getElementById('output').innerText = "/ " + data.result + " /";

        document.getElementById('button_img').src = '/frontend/assets/recording.svg';
        document.getElementById('toggle').classList.remove("toggled");

        document.getElementById('loading').style.display = "none";
        document.getElementById('result_box').style.display = "block";

    };
}

function copy_to_clipboard()
{
    let transcription = document.getElementById('output').innerText;
    navigator.clipboard.writeText(transcription.replaceAll(" ", ""));

    document.getElementById("clipboard_button").classList.add("clipboard");
    document.getElementById("clipboard_button").innerHTML = "Copied!";
}