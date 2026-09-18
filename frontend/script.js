const API_URL = "http://127.0.0.1:8000";


// =========================
// NAVIGATION
// =========================

function showSection(section) {

    document.querySelectorAll(".nav-btn").forEach(button => {
        button.classList.remove("active");
    });

    const buttons = document.querySelectorAll(".nav-btn");

    buttons.forEach(button => {

        if (
            button.textContent
                .toLowerCase()
                .includes(section.toLowerCase())
        ) {
            button.classList.add("active");
        }

    });

    if (section !== "triage") {
        alert(
            section.charAt(0).toUpperCase() +
            section.slice(1) +
            " module coming soon."
        );
    }
}


// =========================
// ASSESS PATIENT
// =========================

document
    .getElementById("assessBtn")
    .addEventListener("click", async function () {

        const button = document.getElementById("assessBtn");


        // =========================
        // GET RAW INPUT VALUES
        // =========================

        const name =
            document.getElementById("name").value.trim();

        const age =
            document.getElementById("age").value;

        const sex =
            document.getElementById("sex").value;

        const symptoms =
            document.getElementById("symptoms").value.trim();

        const disorders =
            document.getElementById("disorders").value.trim();

        const heartRate =
            document.getElementById("heart_rate").value;

        const systolicBP =
            document.getElementById("systolic_bp").value;

        const diastolicBP =
            document.getElementById("diastolic_bp").value;

        const respiratoryRate =
            document.getElementById("respiratory_rate").value;

        const spo2 =
            document.getElementById("spo2").value;

        const temperature =
            document.getElementById("temperature").value;

        const painScore =
            document.getElementById("pain_score").value;

        const gcsScore =
            document.getElementById("gcs_score").value;

        const arrivalMode =
            document.getElementById("arrival_mode").value;


        // =========================
        // VALIDATION
        // =========================

        if (
            !age ||
            !sex ||
            !symptoms ||
            !heartRate ||
            !systolicBP ||
            !diastolicBP ||
            !respiratoryRate ||
            !spo2 ||
            !temperature ||
            painScore === "" ||
            !gcsScore
        ) {

            alert(
                "Please enter all required patient and vital information."
            );

            return;
        }


        // =========================
        // CREATE REQUEST
        // =========================

        const patient = {

            name: name || "Unknown",

            age: Number(age),

            sex: sex,

            symptoms: symptoms,

            disorders: disorders,

            heart_rate: Number(heartRate),

            systolic_bp: Number(systolicBP),

            diastolic_bp: Number(diastolicBP),

            respiratory_rate: Number(respiratoryRate),

            spo2: Number(spo2),

            temperature: Number(temperature),

            pain_score: Number(painScore),

            gcs_score: Number(gcsScore),

            arrival_mode: arrivalMode

        };


        // =========================
        // LOADING
        // =========================

        button.disabled = true;

        button.querySelector("span").textContent =
            "Assessing...";


        try {

            // =========================
            // SEND TO FASTAPI
            // =========================

            const response = await fetch(
                `${API_URL}/patients`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(patient)
                }
            );


            // =========================
            // HANDLE API ERROR
            // =========================

            if (!response.ok) {

                const errorData =
                    await response.json();

                console.error(
                    "Backend error:",
                    errorData
                );

                throw new Error(
                    errorData.detail ||
                    "Assessment failed"
                );
            }


            // =========================
            // GET RESULT
            // =========================

            const result =
                await response.json();

            console.log(
                "MEDORA result:",
                result
            );


            // =========================
            // SHOW RESULT
            // =========================

            const resultSection =
                document.getElementById(
                    "resultSection"
                );

            resultSection.classList.remove(
                "hidden"
            );


            document.getElementById(
                "urgencyResult"
            ).textContent =
                result.urgency;


            document.getElementById(
                "riskScore"
            ).textContent =
                `${result.risk_score}%`;


            document.getElementById(
                "patientId"
            ).textContent =
                result.patient_id;


            // =========================
            // RISK FACTORS
            // =========================

            const riskFactors =
                document.getElementById(
                    "riskFactors"
                );

            riskFactors.innerHTML = "";


            if (
                result.risk_factors &&
                result.risk_factors.length > 0
            ) {

                result.risk_factors.forEach(
                    factor => {

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

            } else {

                const li =
                    document.createElement(
                        "li"
                    );

                li.textContent =
                    "No major warning indicators detected";

                riskFactors.appendChild(li);
            }


            // =========================
            // SCROLL TO RESULT
            // =========================

            resultSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }


        // =========================
        // CONNECTION ERROR
        // =========================

        catch (error) {

            console.error(
                "MEDORA error:",
                error
            );

            alert(
                "Unable to connect to MEDORA backend.\n\n" +
                "Make sure FastAPI is running on:\n" +
                "http://127.0.0.1:8000"
            );

        }


        // =========================
        // RESET BUTTON
        // =========================

        finally {

            button.disabled = false;

            button.querySelector("span").textContent =
                "Assess Patient";

        }

    });