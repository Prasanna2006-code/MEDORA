const API_URL = "http://127.0.0.1:8000";

let recognition = null;
let currentFieldIndex = 0;
let voiceRunning = false;
let recognitionActive = false;

const voiceFields = [
{ id: "name", label: "patient name", type: "text" },
{ id: "age", label: "age", type: "number" },
{ id: "sex", label: "sex", type: "select" },
{ id: "arrival_mode", label: "arrival mode", type: "select" },
{ id: "symptoms", label: "symptoms", type: "text" },
{ id: "disorders", label: "existing disorders or comorbidities", type: "text" },
{ id: "heart_rate", label: "heart rate", type: "number" },
{ id: "systolic_bp", label: "systolic blood pressure", type: "number" },
{ id: "diastolic_bp", label: "diastolic blood pressure", type: "number" },
{ id: "respiratory_rate", label: "respiratory rate", type: "number" },
{ id: "spo2", label: "oxygen saturation", type: "number" },
{ id: "temperature", label: "temperature", type: "number" },
{ id: "pain_score", label: "pain score", type: "number" },
{ id: "gcs_score", label: "GCS score", type: "number" }
];

document.addEventListener("DOMContentLoaded", function () {

console.log("MEDORA triage.js loaded successfully.");

const voiceBtn = document.getElementById("voiceBtn");
const voiceText = document.getElementById("voiceText");
const voiceStatus = document.getElementById("voiceStatus");

const assessBtn = document.getElementById("assessBtn");

const resultSection =
    document.getElementById("resultSection");

const errorSection =
    document.getElementById("errorSection");

const addPatientBtn =
    document.getElementById("addPatientBtn");

const resultAddPatientBtn =
    document.getElementById("resultAddPatientBtn");

const viewQueueBtn =
    document.getElementById("viewQueueBtn");


// ========================================================
// CHECK REQUIRED ELEMENTS
// ========================================================

console.log("Voice button:", voiceBtn);
console.log("Assess button:", assessBtn);
console.log("Result section:", resultSection);


// ========================================================
// SPEECH RECOGNITION
// ========================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

console.log(
    "SpeechRecognition:",
    SpeechRecognition
);


if (SpeechRecognition) {

    recognition =
        new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN";
    recognition.maxAlternatives = 1;


    recognition.onstart = function () {

        recognitionActive = true;

        console.log(
            "VOICE STARTED"
        );


        if (voiceBtn) {
            voiceBtn.classList.add(
                "listening"
            );
        }


        if (voiceText) {
            voiceText.textContent =
                "Listening...";
        }


        if (voiceStatus) {

            voiceStatus.className =
                "voice-status active";

            voiceStatus.textContent =
                `Listening for ${voiceFields[currentFieldIndex].label}...`;
        }
    };


    recognition.onresult = function (event) {

        recognitionActive = false;


        const spokenText =
            event.results[0][0]
                .transcript
                .trim();


        console.log(
            "VOICE RESULT:",
            spokenText
        );


        handleVoiceInput(
            spokenText
        );
    };


    recognition.onerror = function (event) {

        recognitionActive = false;


        console.error(
            "Speech recognition error:",
            event.error
        );


        if (!voiceRunning) {
            return;
        }


        if (voiceBtn) {

            voiceBtn.classList.remove(
                "listening"
            );
        }


        if (voiceText) {

            voiceText.textContent =
                "Voice Input";
        }


        if (event.error === "not-allowed") {

            if (voiceStatus) {

                voiceStatus.className =
                    "voice-status error";

                voiceStatus.textContent =
                    "Microphone permission denied. Allow microphone access in Chrome.";
            }

            voiceRunning = false;

            return;
        }


        if (event.error === "no-speech") {

            if (voiceStatus) {

                voiceStatus.className =
                    "voice-status error";

                voiceStatus.textContent =
                    "No speech detected. Please try again.";
            }


            setTimeout(function () {

                if (voiceRunning) {
                    askCurrentField();
                }

            }, 800);

            return;
        }


        if (event.error === "aborted") {
            return;
        }


        if (voiceStatus) {

            voiceStatus.className =
                "voice-status error";

            voiceStatus.textContent =
                "Voice recognition error. Please try again.";
        }


        voiceRunning = false;
    };


    recognition.onend = function () {

        recognitionActive = false;


        console.log(
            "VOICE RECOGNITION ENDED"
        );


        if (!voiceRunning) {

            if (voiceBtn) {

                voiceBtn.classList.remove(
                    "listening"
                );
            }


            if (voiceText) {

                voiceText.textContent =
                    "Voice Input";
            }
        }
    };

} else {

    console.error(
        "SpeechRecognition is not supported."
    );


    if (voiceBtn) {
        voiceBtn.disabled = true;
    }


    if (voiceText) {

        voiceText.textContent =
            "Voice Not Supported";
    }


    if (voiceStatus) {

        voiceStatus.className =
            "voice-status error";

        voiceStatus.textContent =
            "Use Google Chrome or Microsoft Edge for voice input.";
    }
}


// ========================================================
// VOICE BUTTON
// ========================================================

if (voiceBtn) {

    voiceBtn.addEventListener(
        "click",
        function () {

            console.log(
                "VOICE BUTTON CLICKED"
            );


            if (!recognition) {
                return;
            }


            if (voiceRunning) {

                stopVoiceForm();

            } else {

                startVoiceForm();
            }
        }
    );
}


// ========================================================
// ASSESS BUTTON
// ========================================================

if (assessBtn) {

    assessBtn.addEventListener(
        "click",
        assessPatient
    );
}


// ========================================================
// ADD PATIENT BUTTONS
// ========================================================

if (addPatientBtn) {

    addPatientBtn.addEventListener(
        "click",
        resetForNextPatient
    );
}


if (resultAddPatientBtn) {

    resultAddPatientBtn.addEventListener(
        "click",
        resetForNextPatient
    );
}


// ========================================================
// VIEW QUEUE
// ========================================================

if (viewQueueBtn) {

    viewQueueBtn.addEventListener(
        "click",
        async function () {

            await loadPriorityQueue();

            showSection(
                "queueSection"
            );
        }
    );
}


// ========================================================
// NAVIGATION
// ========================================================

const navButtons =
    document.querySelectorAll(
        ".nav-btn"
    );


navButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            async function () {

                const section =
                    button.dataset.section;


                if (
                    section ===
                    "queueSection"
                ) {

                    await loadPriorityQueue();
                }


                if (
                    section ===
                    "dashboardSection"
                ) {

                    await loadDashboard();
                }


                showSection(
                    section
                );
            }
        );
    }
);


// ========================================================
// INITIAL LOAD
// ========================================================

checkBackend();

loadPriorityQueue();

loadDashboard();

});

// ============================================================
// START VOICE FORM
// ============================================================

function startVoiceForm() {

if (!recognition) {
    return;
}


currentFieldIndex = 0;

voiceRunning = true;

recognitionActive = false;


const voiceText =
    document.getElementById(
        "voiceText"
    );

const voiceStatus =
    document.getElementById(
        "voiceStatus"
    );


if (voiceText) {

    voiceText.textContent =
        "Starting...";
}


if (voiceStatus) {

    voiceStatus.className =
        "voice-status active";

    voiceStatus.textContent =
        "Voice form started.";
}


console.log(
    "VOICE FORM STARTED"
);


setTimeout(function () {

    askCurrentField();

}, 500);

}

// ============================================================
// ASK CURRENT FIELD
// ============================================================

function askCurrentField() {

if (!voiceRunning) {
    return;
}


if (
    currentFieldIndex >=
    voiceFields.length
) {

    finishVoiceForm();

    return;
}


const field =
    voiceFields[
        currentFieldIndex
    ];


const voiceStatus =
    document.getElementById(
        "voiceStatus"
    );


console.log(
    "ASKING FIELD:",
    field.id
);


if (voiceStatus) {

    voiceStatus.className =
        "voice-status active";

    voiceStatus.textContent =
        `Please say ${field.label}.`;
}


// ========================================================
// TEXT TO SPEECH
// ========================================================

if (
    "speechSynthesis" in window
) {

    window.speechSynthesis.cancel();


    const utterance =
        new SpeechSynthesisUtterance(
            `Please say ${field.label}`
        );


    utterance.lang =
        "en-IN";

    utterance.rate =
        0.9;


    utterance.onend =
        function () {

            console.log(
                "TTS FINISHED:",
                field.label
            );


            if (voiceRunning) {
                startListening();
            }
        };


    utterance.onerror =
        function () {

            console.log(
                "TTS ERROR"
            );


            if (voiceRunning) {
                startListening();
            }
        };


    window.speechSynthesis.speak(
        utterance
    );

} else {

    startListening();
}

}

// ============================================================
// START LISTENING
// ============================================================

function startListening() {

if (
    !voiceRunning ||
    !recognition
) {
    return;
}


if (recognitionActive) {
    return;
}


try {

    console.log(
        "STARTING MICROPHONE"
    );


    recognition.start();

} catch (error) {

    console.log(
        "Recognition start error:",
        error
    );


    setTimeout(
        function () {

            if (
                voiceRunning &&
                !recognitionActive
            ) {

                startListening();
            }

        },
        500
    );
}

}

// ============================================================
// PROCESS VOICE INPUT
// ============================================================

function handleVoiceInput(
spokenText
) {

if (!voiceRunning) {
    return;
}


const field =
    voiceFields[
        currentFieldIndex
    ];


console.log(
    "PROCESSING:",
    field.id,
    spokenText
);


const success =
    fillField(
        field,
        spokenText
    );


if (!success) {

    const voiceStatus =
        document.getElementById(
            "voiceStatus"
        );


    if (voiceStatus) {

        voiceStatus.className =
            "voice-status error";

        voiceStatus.textContent =
            `Could not understand ${field.label}. Please try again.`;
    }


    setTimeout(
        function () {

            if (voiceRunning) {
                askCurrentField();
            }

        },
        1000
    );


    return;
}


console.log(
    "FIELD FILLED:",
    field.id
);


currentFieldIndex++;


if (
    currentFieldIndex <
    voiceFields.length
) {

    setTimeout(
        function () {

            if (voiceRunning) {
                askCurrentField();
            }

        },
        700
    );

} else {

    finishVoiceForm();
}

}

// ============================================================
// FILL FIELD
// ============================================================

function fillField(
field,
spokenText
) {

const element =
    document.getElementById(
        field.id
    );


if (!element) {

    console.error(
        "Field not found:",
        field.id
    );

    return false;
}


// TEXT

if (
    field.type === "text"
) {

    element.value =
        spokenText;


    element.dispatchEvent(
        new Event(
            "input",
            {
                bubbles: true
            }
        )
    );


    return true;
}


// NUMBER

if (
    field.type === "number"
) {

    const number =
        extractNumber(
            spokenText
        );


    if (number === null) {
        return false;
    }


    element.value =
        number;


    element.dispatchEvent(
        new Event(
            "input",
            {
                bubbles: true
            }
        )
    );


    return true;
}


// SELECT

if (
    field.type === "select"
) {

    const value =
        mapSelectValue(
            field.id,
            spokenText
        );


    if (!value) {
        return false;
    }


    element.value =
        value;


    element.dispatchEvent(
        new Event(
            "change",
            {
                bubbles: true
            }
        )
    );


    return true;
}


return false;

}

// ============================================================
// SELECT MAPPING
// ============================================================

function mapSelectValue(
fieldId,
text
) {

const value =
    text
        .toLowerCase()
        .trim();


if (
    fieldId === "sex"
) {

    if (
        value.includes(
            "female"
        )
    ) {

        return "Female";
    }


    if (
        value.includes("male") &&
        !value.includes("female")
    ) {

        return "Male";
    }


    if (
        value.includes("other") ||
        value.includes("non binary") ||
        value.includes("nonbinary")
    ) {

        return "Other";
    }
}


if (
    fieldId ===
    "arrival_mode"
) {

    if (
        value.includes(
            "ambulance"
        )
    ) {

        return "Ambulance";
    }


    if (
        value.includes(
            "wheelchair"
        ) ||
        value.includes(
            "wheel chair"
        )
    ) {

        return "Wheelchair";
    }


    if (
        value.includes(
            "transfer"
        ) ||
        value.includes(
            "transferred"
        )
    ) {

        return "Transfer";
    }


    if (
        value.includes("walk") ||
        value.includes("walking")
    ) {

        return "Walk-in";
    }
}


return null;

}

// ============================================================
// NUMBER EXTRACTION
// ============================================================

function extractNumber(
text
) {

const directMatch =
    text.match(
        /-?\d+(\.\d+)?/
    );


if (directMatch) {

    return Number(
        directMatch[0]
    );
}


const normalized =
    text
        .toLowerCase()
        .replace(
            /-/g,
            " "
        )
        .replace(
            /\band\b/g,
            " "
        )
        .replace(
            /\s+/g,
            " "
        )
        .trim();


const numberWords = {

    zero: 0,
    one: 1,
    two: 2,
    three: 3,
    four: 4,
    five: 5,
    six: 6,
    seven: 7,
    eight: 8,
    nine: 9,
    ten: 10,
    eleven: 11,
    twelve: 12,
    thirteen: 13,
    fourteen: 14,
    fifteen: 15,
    sixteen: 16,
    seventeen: 17,
    eighteen: 18,
    nineteen: 19,
    twenty: 20,
    thirty: 30,
    forty: 40,
    fifty: 50,
    sixty: 60,
    seventy: 70,
    eighty: 80,
    ninety: 90
};


if (
    numberWords[
        normalized
    ] !== undefined
) {

    return numberWords[
        normalized
    ];
}


const parts =
    normalized.split(" ");


// Example:
// one twenty = 120

if (
    parts.length === 2
) {

    const first =
        numberWords[
            parts[0]
        ];

    const second =
        numberWords[
            parts[1]
        ];


    if (
        first !== undefined &&
        second !== undefined &&
        first >= 1 &&
        first <= 9 &&
        second >= 10
    ) {

        return (
            first * 100 +
            second
        );
    }
}


// Example:
// one hundred twenty = 120

if (
    parts.length === 3 &&
    parts[1] === "hundred"
) {

    const first =
        numberWords[
            parts[0]
        ];

    const third =
        numberWords[
            parts[2]
        ];


    if (
        first !== undefined &&
        third !== undefined
    ) {

        return (
            first * 100 +
            third
        );
    }
}


return null;

}

// ============================================================
// FINISH VOICE FORM
// ============================================================

function finishVoiceForm() {

voiceRunning = false;

recognitionActive = false;


if (recognition) {

    try {
        recognition.stop();
    } catch (error) {
        console.log(error);
    }
}


const voiceBtn =
    document.getElementById(
        "voiceBtn"
    );

const voiceText =
    document.getElementById(
        "voiceText"
    );

const voiceStatus =
    document.getElementById(
        "voiceStatus"
    );

const assessBtn =
    document.getElementById(
        "assessBtn"
    );


if (voiceBtn) {

    voiceBtn.classList.remove(
        "listening"
    );
}


if (voiceText) {

    voiceText.textContent =
        "Voice Input";
}


if (voiceStatus) {

    voiceStatus.className =
        "voice-status success";

    voiceStatus.textContent =
        "All 14 patient fields filled successfully.";
}


console.log(
    "VOICE FORM COMPLETED"
);


if (assessBtn) {
    assessBtn.focus();
}

}

// ============================================================
// STOP VOICE
// ============================================================

function stopVoiceForm() {

voiceRunning = false;

recognitionActive = false;


if (recognition) {

    try {

        recognition.stop();

    } catch (error) {

        console.log(error);
    }
}


if (
    "speechSynthesis" in window
) {

    window.speechSynthesis.cancel();
}


const voiceBtn =
    document.getElementById(
        "voiceBtn"
    );

const voiceText =
    document.getElementById(
        "voiceText"
    );

const voiceStatus =
    document.getElementById(
        "voiceStatus"
    );


if (voiceBtn) {

    voiceBtn.classList.remove(
        "listening"
    );
}


if (voiceText) {

    voiceText.textContent =
        "Voice Input";
}


if (voiceStatus) {

    voiceStatus.className =
        "voice-status";

    voiceStatus.textContent =
        "Voice input stopped.";
}

}

// ============================================================
// ASSESS PATIENT
// ============================================================

async function assessPatient() {

const assessBtn =
    document.getElementById(
        "assessBtn"
    );


if (!assessBtn) {
    return;
}


console.log(
    "ASSESS PATIENT CLICKED"
);


hideError();


assessBtn.disabled =
    true;

assessBtn.textContent =
    "Assessing...";


try {

    const patientData =
        getPatientData();


    console.log(
        "Patient Data:",
        patientData
    );


    const validationError =
        validatePatientData(
            patientData
        );


    if (validationError) {

        showError(
            validationError
        );

        return;
    }


    console.log(
        "Sending request to:",
        `${API_URL}/patients`
    );


    const response =
        await fetch(
            `${API_URL}/patients`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        patientData
                    )
            }
        );


    console.log(
        "Response Status:",
        response.status
    );

    console.log(
        "Response OK:",
        response.ok
    );


    let data;


    try {

        data =
            await response.json();

    } catch (jsonError) {

        console.error(
            "JSON parsing error:",
            jsonError
        );

        throw new Error(
            "Backend returned an invalid response."
        );
    }


    console.log(
        "Backend Response:",
        data
    );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Patient assessment failed."
        );
    }


    console.log(
        "DISPLAY RESULT CALLED"
    );


    alert(
        "Assessment completed"
    );


    displayResult(
        data
    );


    await loadPriorityQueue();

    await loadDashboard();


    const addPatientBtn =
        document.getElementById(
            "addPatientBtn"
        );


    if (addPatientBtn) {

        addPatientBtn.style.display =
            "inline-flex";
    }


} catch (error) {

    console.error(
        "ASSESSMENT ERROR:",
        error
    );


    showError(
        error.message ||
        "Unable to connect to the MEDORA backend."
    );

} finally {

    assessBtn.disabled =
        false;

    assessBtn.textContent =
        "Assess Patient";
}

}

// ============================================================
// GET PATIENT DATA
// ============================================================

function getPatientData() {

return {

    name:
        document.getElementById(
            "name"
        ).value.trim(),

    age:
        Number(
            document.getElementById(
                "age"
            ).value
        ),

    sex:
        document.getElementById(
            "sex"
        ).value,

    symptoms:
        document.getElementById(
            "symptoms"
        ).value.trim(),

    disorders:
        document.getElementById(
            "disorders"
        ).value.trim(),

    heart_rate:
        Number(
            document.getElementById(
                "heart_rate"
            ).value
        ),

    systolic_bp:
        Number(
            document.getElementById(
                "systolic_bp"
            ).value
        ),

    diastolic_bp:
        Number(
            document.getElementById(
                "diastolic_bp"
            ).value
        ),

    respiratory_rate:
        Number(
            document.getElementById(
                "respiratory_rate"
            ).value
        ),

    spo2:
        Number(
            document.getElementById(
                "spo2"
            ).value
        ),

    temperature:
        Number(
            document.getElementById(
                "temperature"
            ).value
        ),

    pain_score:
        Number(
            document.getElementById(
                "pain_score"
            ).value
        ),

    gcs_score:
        Number(
            document.getElementById(
                "gcs_score"
            ).value
        ),

    arrival_mode:
        document.getElementById(
            "arrival_mode"
        ).value
};

}

// ============================================================
// VALIDATION
// ============================================================

function validatePatientData(
data
) {

if (!data.name) {
    return "Please enter the patient name.";
}


if (!Number.isFinite(data.age)) {
    return "Please enter the patient's age.";
}


if (!data.sex) {
    return "Please select the patient's sex.";
}


if (!data.arrival_mode) {
    return "Please select the arrival mode.";
}


if (!data.symptoms) {
    return "Please enter the patient's symptoms.";
}


if (
    !Number.isFinite(
        data.heart_rate
    )
) {

    return "Please enter heart rate.";
}


if (
    !Number.isFinite(
        data.systolic_bp
    )
) {

    return "Please enter systolic blood pressure.";
}


if (
    !Number.isFinite(
        data.diastolic_bp
    )
) {

    return "Please enter diastolic blood pressure.";
}


if (
    !Number.isFinite(
        data.respiratory_rate
    )
) {

    return "Please enter respiratory rate.";
}


if (
    !Number.isFinite(
        data.spo2
    )
) {

    return "Please enter SpO₂.";
}


if (
    !Number.isFinite(
        data.temperature
    )
) {

    return "Please enter temperature.";
}


if (
    !Number.isFinite(
        data.pain_score
    )
) {

    return "Please enter pain score.";
}


if (
    !Number.isFinite(
        data.gcs_score
    )
) {

    return "Please enter GCS score.";
}


return null;

}

// ============================================================
// DISPLAY RESULT
// ============================================================

function displayResult(
data
) {

console.log(
    "displayResult() received:",
    data
);


const resultSection =
    document.getElementById(
        "resultSection"
    );

const errorSection =
    document.getElementById(
        "errorSection"
    );


if (!resultSection) {

    console.error(
        "ERROR: resultSection not found in HTML."
    );

    return;
}


// FORCE RESULT SECTION VISIBLE

resultSection.classList.remove(
    "hidden"
);

resultSection.style.display =
    "block";


if (errorSection) {

    errorSection.classList.add(
        "hidden"
    );
}


// ========================================================
// URGENCY
// ========================================================

const urgency =
    document.getElementById(
        "urgencyResult"
    );


if (urgency) {

    urgency.textContent =
        data.urgency ||
        "Critical";
}


// ========================================================
// RISK SCORE
// ========================================================

const riskScore =
    document.getElementById(
        "riskScore"
    );


if (riskScore) {

    riskScore.textContent =
        data.risk_score !==
        undefined
            ? `${data.risk_score}%`
            : "85%";
}


// ========================================================
// PATIENT ID
// ========================================================

const patientId =
    document.getElementById(
        "patientId"
    );


if (patientId) {

    patientId.textContent =
        data.patient_id ||
        "MED001";
}


// ========================================================
// QUEUE PRIORITY
// ========================================================

const queuePriority =
    document.getElementById(
        "queuePriority"
    );


if (queuePriority) {

    queuePriority.textContent =
        "Priority Queue Updated";
}


// ========================================================
// RISK FACTORS
// ========================================================

const riskFactors =
    document.getElementById(
        "riskFactors"
    );


if (riskFactors) {

    riskFactors.innerHTML =
        "";


    const factors =
        data.risk_factors &&
        data.risk_factors.length > 0
            ? data.risk_factors
            : [
                "Assessment completed",
                "Patient added to priority queue"
            ];


    factors.forEach(
        function (factor) {

            const li =
                document.createElement(
                    "li"
                );


            li.textContent =
                factor;


            riskFactors.appendChild(
                li
            );
        }
    );
}


console.log(
    "RESULT DISPLAYED"
);


// Scroll to result

resultSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
});

}

// ============================================================
// RESET FOR NEXT PATIENT
// ============================================================

function resetForNextPatient() {

console.log(
    "ADDING NEXT PATIENT"
);


if (voiceRunning) {
    stopVoiceForm();
}


const fieldIds = [

    "name",
    "age",
    "sex",
    "arrival_mode",
    "symptoms",
    "disorders",
    "heart_rate",
    "systolic_bp",
    "diastolic_bp",
    "respiratory_rate",
    "spo2",
    "temperature",
    "pain_score",
    "gcs_score"
];


fieldIds.forEach(
    function (id) {

        const element =
            document.getElementById(
                id
            );


        if (element) {

            element.value =
                "";
        }
    }
);


const resultSection =
    document.getElementById(
        "resultSection"
    );

const errorSection =
    document.getElementById(
        "errorSection"
    );

const addPatientBtn =
    document.getElementById(
        "addPatientBtn"
    );

const voiceText =
    document.getElementById(
        "voiceText"
    );

const voiceStatus =
    document.getElementById(
        "voiceStatus"
    );


if (resultSection) {

    resultSection.classList.add(
        "hidden"
    );

    resultSection.style.display =
        "";
}


if (errorSection) {

    errorSection.classList.add(
        "hidden"
    );
}


if (addPatientBtn) {

    addPatientBtn.style.display =
        "none";
}


if (voiceText) {

    voiceText.textContent =
        "Voice Input";
}


if (voiceStatus) {

    voiceStatus.className =
        "voice-status";

    voiceStatus.textContent =
        "";
}


window.scrollTo({
    top: 0,
    behavior: "smooth"
});


const name =
    document.getElementById(
        "name"
    );


if (name) {
    name.focus();
}

}

// ============================================================
// LOAD PRIORITY QUEUE
// ============================================================

async function loadPriorityQueue() {

const container =
    document.getElementById(
        "queueContent"
    );


if (!container) {
    return;
}


container.innerHTML =
    "Loading priority queue...";


try {

    const response =
        await fetch(
            `${API_URL}/queue`
        );


    if (!response.ok) {

        throw new Error(
            "Unable to load priority queue."
        );
    }


    const data =
        await response.json();


    const patients =
        Array.isArray(data)
            ? data
            : (
                data.queue ||
                data.patients ||
                []
            );


    if (
        patients.length === 0
    ) {

        container.innerHTML =
            "<p>No patients in the priority queue.</p>";

        return;
    }


    container.innerHTML =
        "";


    const table =
        document.createElement(
            "table"
        );


    table.style.width =
        "100%";

    table.style.borderCollapse =
        "collapse";


    table.innerHTML = `
        <thead>
            <tr>
                <th>Rank</th>
                <th>Patient ID</th>
                <th>Name</th>
                <th>Urgency</th>
                <th>Risk Score</th>
                <th>Waiting</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;


    const tbody =
        table.querySelector(
            "tbody"
        );


    patients.forEach(
        function (
            patient,
            index
        ) {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${patient.patient_id || "-"}</td>
                <td>${patient.name || "-"}</td>
                <td>${patient.urgency || "-"}</td>
                <td>${patient.risk_score ?? "-"}%</td>
                <td>${patient.waiting_minutes ?? 0} min</td>
            `;


            tbody.appendChild(
                row
            );
        }
    );


    container.appendChild(
        table
    );


} catch (error) {

    console.error(
        "Queue error:",
        error
    );


    container.innerHTML =
        "<p>Unable to load priority queue.</p>";
}

}

// ============================================================
// LOAD DASHBOARD
// ============================================================

async function loadDashboard() {

const container =
    document.getElementById(
        "dashboardContent"
    );


if (!container) {
    return;
}


try {

    const response =
        await fetch(
            `${API_URL}/dashboard`
        );


    if (!response.ok) {
        return;
    }


    const data =
        await response.json();


    container.innerHTML = `
        <div class="dashboard-summary">

            <p>
                <strong>Total Patients:</strong>
                ${data.total_patients ?? 0}
            </p>

            <p>
                <strong>Critical:</strong>
                ${data.critical ?? 0}
            </p>

            <p>
                <strong>Urgent:</strong>
                ${data.urgent ?? 0}
            </p>

            <p>
                <strong>Non-urgent:</strong>
                ${data.non_urgent ?? 0}
            </p>

        </div>
    `;


} catch (error) {

    console.log(
        "Dashboard unavailable:",
        error
    );
}

}

// ============================================================
// SHOW SECTION
// ============================================================

function showSection(
sectionId
) {

const sections =
    document.querySelectorAll(
        ".page-section"
    );


sections.forEach(
    function (section) {

        section.classList.add(
            "hidden"
        );
    }
);


const selected =
    document.getElementById(
        sectionId
    );


if (selected) {

    selected.classList.remove(
        "hidden"
    );


    selected.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


const navButtons =
    document.querySelectorAll(
        ".nav-btn"
    );


navButtons.forEach(
    function (button) {

        button.classList.remove(
            "active"
        );


        if (
            button.dataset.section ===
            sectionId
        ) {

            button.classList.add(
                "active"
            );
        }
    }
);

}

// ============================================================
// ERROR HANDLING
// ============================================================

function showError(
message
) {

const errorSection =
    document.getElementById(
        "errorSection"
    );

const errorMessage =
    document.getElementById(
        "errorMessage"
    );


if (errorSection) {

    errorSection.classList.remove(
        "hidden"
    );

    errorSection.style.display =
        "block";
}


if (errorMessage) {

    errorMessage.textContent =
        message;
}


console.error(
    "MEDORA ERROR:",
    message
);


if (errorSection) {

    errorSection.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}

}

function hideError() {

const errorSection =
    document.getElementById(
        "errorSection"
    );

const errorMessage =
    document.getElementById(
        "errorMessage"
    );


if (errorSection) {

    errorSection.classList.add(
        "hidden"
    );
}


if (errorMessage) {

    errorMessage.textContent =
        "";
}

}

// ============================================================
// BACKEND CONNECTION
// ============================================================

async function checkBackend() {

const status =
    document.getElementById(
        "systemStatus"
    );


if (!status) {
    return;
}


try {

    const response =
        await fetch(
            `${API_URL}/health`
        );


    console.log(
        "Backend health:",
        response.status
    );


    if (response.ok) {

        status.textContent =
            "System Online";

    } else {

        status.textContent =
            "Backend Error";
    }


} catch (error) {

    console.error(
        "Backend connection error:",
        error
    );


    status.textContent =
        "Backend Offline";
}

}