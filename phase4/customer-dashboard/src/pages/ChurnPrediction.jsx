import { useState } from "react";
import api from "../api";


function ChurnPrediction() {

    // ========================================================
    // FORM STATE
    // ========================================================

    const [formData, setFormData] = useState({
        tenure: "",
        monthly_charges: "",
        contract_type: "Month-to-month",
        service_count: 0
    });


    // ========================================================
    // RESULT STATE
    // ========================================================

    const [result, setResult] = useState(null);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");


    // ========================================================
    // HANDLE INPUT CHANGE
    // ========================================================

    const handleChange = (e) => {

        const { name, value } = e.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value
        }));

    };


    // ========================================================
    // SUBMIT FORM
    // ========================================================

    const handleSubmit = async (e) => {

        e.preventDefault();

        setLoading(true);

        setError("");

        setResult(null);


        try {

            // ------------------------------------------------
            // Convert numeric fields from strings to numbers
            // ------------------------------------------------

            const requestData = {
                tenure: Number(formData.tenure),

                monthly_charges:
                    Number(formData.monthly_charges),

                contract_type:
                    formData.contract_type,

                service_count:
                    Number(formData.service_count)
            };


            console.log(
                "Prediction request:",
                requestData
            );


            // ------------------------------------------------
            // POST /predict-churn
            // ------------------------------------------------

            const response = await api.post(
                "/predict-churn",
                requestData
            );


            console.log(
                "Prediction response:",
                response.data
            );


            setResult(response.data);

        }

        catch (e) {

            console.error(
                "Prediction Error:",
                e
            );


            // ------------------------------------------------
            // Pydantic 422 validation error
            // ------------------------------------------------

            if (e.response?.status === 422) {

                const detail = e.response?.data?.detail;


                if (Array.isArray(detail)) {

                    const messages = detail.map(
                        (item) => item.msg
                    );


                    setError(
                        messages.join(", ")
                    );

                }

                else {

                    setError(
                        detail ||
                        "Invalid input"
                    );

                }

            }

            else if (e.response?.status === 401) {

                setError(
                    "Unauthorized. Please check your API key."
                );

            }

            else {

                setError(
                    "Prediction request failed."
                );

            }

        }

        finally {

            setLoading(false);

        }

    };


    // ========================================================
    // DETERMINE RISK LEVEL
    // ========================================================

    const getRiskLevel = (score) => {

        if (score < 0.3) {

            return "Low Risk";

        }

        if (score <= 0.6) {

            return "Medium Risk";

        }

        return "High Risk";

    };


    // ========================================================
    // RISK COLOR
    // ========================================================

    const getRiskColor = (score) => {

        if (score < 0.3) {

            return "#16a34a";

        }

        if (score <= 0.6) {

            return "#d97706";

        }

        return "#dc2626";

    };


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div style={styles.container}>

            <h1>Churn Prediction</h1>

            <p style={styles.description}>
                Enter customer information to estimate their
                likelihood of churn.
            </p>


            {/* =================================================
                FORM
            ================================================= */}

            <form
                onSubmit={handleSubmit}
                style={styles.form}
            >

                {/* =================================================
                    TENURE
                ================================================= */}

                <div style={styles.field}>

                    <label style={styles.label}>
                        Tenure (months)
                    </label>

                    <input
                        type="number"
                        name="tenure"
                        min="0"
                        max="100"
                        value={formData.tenure}
                        onChange={handleChange}
                        placeholder="e.g. 24"
                        required
                        style={styles.input}
                    />

                </div>


                {/* =================================================
                    MONTHLY CHARGES
                ================================================= */}

                <div style={styles.field}>

                    <label style={styles.label}>
                        Monthly Charges
                    </label>

                    <input
                        type="number"
                        name="monthly_charges"
                        min="0.01"
                        step="0.01"
                        value={
                            formData.monthly_charges
                        }
                        onChange={handleChange}
                        placeholder="e.g. 75.50"
                        required
                        style={styles.input}
                    />

                </div>


                {/* =================================================
                    CONTRACT TYPE
                ================================================= */}

                <div style={styles.field}>

                    <label style={styles.label}>
                        Contract Type
                    </label>

                    <select
                        name="contract_type"
                        value={
                            formData.contract_type
                        }
                        onChange={handleChange}
                        style={styles.input}
                    >

                        <option value="Month-to-month">
                            Month-to-month
                        </option>

                        <option value="One year">
                            One year
                        </option>

                        <option value="Two year">
                            Two year
                        </option>

                    </select>

                </div>


                {/* =================================================
                    SERVICE COUNT
                ================================================= */}

                <div style={styles.field}>

                    <label style={styles.label}>
                        Service Count (0–6)
                    </label>

                    <input
                        type="number"
                        name="service_count"
                        min="0"
                        max="6"
                        value={
                            formData.service_count
                        }
                        onChange={handleChange}
                        required
                        style={styles.input}
                    />

                </div>


                {/* =================================================
                    SUBMIT
                ================================================= */}

                <button
                    type="submit"
                    disabled={loading}
                    style={styles.button}
                >

                    {loading
                        ? "Predicting..."
                        : "Predict Churn"}

                </button>

            </form>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div style={styles.error}>

                    <strong>Error:</strong>{" "}

                    {error}

                </div>

            )}


            {/* =================================================
                RESULT
            ================================================= */}

            {result && (

                <div style={styles.resultCard}>

                    <h2>
                        Prediction Result
                    </h2>


                    {/* =============================================
                        RISK SCORE
                    ============================================= */}

                    <div
                        style={{
                            ...styles.riskCircle,

                            borderColor:
                                getRiskColor(
                                    result.risk_score
                                )
                        }}
                    >

                        <span
                            style={{
                                ...styles.riskScore,

                                color:
                                    getRiskColor(
                                        result.risk_score
                                    )
                            }}
                        >

                            {(
                                result.risk_score * 100
                            ).toFixed(1)}%

                        </span>

                        <span style={styles.riskLabel}>
                            Churn Risk
                        </span>

                    </div>


                    {/* =============================================
                        RISK LEVEL
                    ============================================= */}

                    <div
                        style={{
                            ...styles.riskBadge,

                            backgroundColor:
                                getRiskColor(
                                    result.risk_score
                                )
                        }}
                    >

                        {getRiskLevel(
                            result.risk_score
                        )}

                    </div>


                    {/* =============================================
                        PREDICTION
                    ============================================= */}

                    <div style={styles.resultRow}>

                        <span style={styles.resultLabel}>
                            Prediction
                        </span>

                        <span>
                            {result.prediction}
                        </span>

                    </div>


                    {/* =============================================
                        CUSTOMER ID
                    ============================================= */}

                    <div style={styles.resultRow}>

                        <span style={styles.resultLabel}>
                            Customer ID
                        </span>

                        <span>
                            {result.customer_id}
                        </span>

                    </div>


                    {/* =============================================
                        NOTE
                    ============================================= */}

                    <p style={styles.note}>

                        {result.note}

                    </p>

                </div>

            )}

        </div>

    );

}


// ============================================================
// STYLES
// ============================================================

const styles = {

    container: {
        maxWidth: "700px",
        margin: "40px auto",
        padding: "20px",
        fontFamily: "Arial, sans-serif"
    },


    description: {
        color: "#666",
        marginBottom: "30px"
    },


    form: {
        padding: "25px",
        border: "1px solid #ddd",
        borderRadius: "10px",
        boxShadow:
            "0 2px 8px rgba(0, 0, 0, 0.08)"
    },


    field: {
        marginBottom: "20px"
    },


    label: {
        display: "block",
        fontWeight: "bold",
        marginBottom: "8px"
    },


    input: {
        width: "100%",
        boxSizing: "border-box",
        padding: "12px",
        fontSize: "16px",
        border: "1px solid #ccc",
        borderRadius: "6px"
    },


    button: {
        width: "100%",
        padding: "13px",
        fontSize: "16px",
        border: "none",
        borderRadius: "6px",
        cursor: "pointer",
        marginTop: "10px"
    },


    error: {
        marginTop: "20px",
        padding: "15px",
        borderRadius: "6px",
        backgroundColor: "#fee2e2",
        color: "#991b1b"
    },


    resultCard: {
        marginTop: "30px",
        padding: "30px",
        border: "1px solid #ddd",
        borderRadius: "10px",
        textAlign: "center",
        boxShadow:
            "0 2px 8px rgba(0, 0, 0, 0.08)"
    },


    riskCircle: {
        width: "160px",
        height: "160px",
        border: "10px solid",
        borderRadius: "50%",
        margin: "25px auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        boxSizing: "border-box"
    },


    riskScore: {
        fontSize: "30px",
        fontWeight: "bold"
    },


    riskLabel: {
        fontSize: "13px",
        color: "#666",
        marginTop: "5px"
    },


    riskBadge: {
        display: "inline-block",
        color: "white",
        padding: "8px 18px",
        borderRadius: "20px",
        fontWeight: "bold",
        marginBottom: "25px"
    },


    resultRow: {
        display: "flex",
        justifyContent: "space-between",
        padding: "14px 0",
        borderBottom: "1px solid #eee",
        textAlign: "left"
    },


    resultLabel: {
        fontWeight: "bold"
    },


    note: {
        marginTop: "25px",
        color: "#666",
        fontSize: "14px"
    }

};


export default ChurnPrediction;