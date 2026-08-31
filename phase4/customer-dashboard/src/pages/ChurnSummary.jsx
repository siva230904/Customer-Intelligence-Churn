import { useEffect, useState } from "react";
import api from "../api";


function ChurnSummary() {

    // ========================================================
    // STATE
    // ========================================================

    const [data, setData] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    // ========================================================
    // FETCH CHURN SUMMARY
    // ========================================================

    useEffect(() => {

        const fetchChurnSummary = async () => {

            try {

                const response = await api.get(
                    "/churn/summary"
                );

                console.log(
                    "Churn Summary:",
                    response.data
                );

                setData(response.data);

            }

            catch (e) {

                console.error(
                    "Churn Summary Error:",
                    e
                );

                if (e.response?.status === 401) {

                    setError(
                        "Unauthorized. Please check your API key."
                    );

                }

                else {

                    setError(
                        "Failed to load churn summary."
                    );

                }

            }

            finally {

                setLoading(false);

            }

        };


        fetchChurnSummary();

    }, []);


    // ========================================================
    // LOADING
    // ========================================================

    if (loading) {

        return (

            <div style={styles.container}>

                <h1>Churn Analytics</h1>

                <p>Loading churn data...</p>

            </div>

        );

    }


    // ========================================================
    // ERROR
    // ========================================================

    if (error) {

        return (

            <div style={styles.container}>

                <h1>Churn Analytics</h1>

                <div style={styles.error}>
                    {error}
                </div>

            </div>

        );

    }


    // ========================================================
    // DATA SAFETY CHECK
    // ========================================================

    if (!data) {

        return null;

    }


    // ========================================================
    // DESTRUCTURE API RESPONSE
    // ========================================================

    const {
        total_customers,
        churned,
        churn_rate,
        by_contract
    } = data;


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div style={styles.container}>

            {/* =================================================
                PAGE HEADER
            ================================================= */}

            <h1>Churn Analytics</h1>

            <p style={styles.description}>
                Monitor customer churn and compare churn rates
                across different contract types.
            </p>


            {/* =================================================
                KPI CARDS
            ================================================= */}

            <div style={styles.metricsContainer}>

                {/* Total Customers */}

                <div style={styles.metricCard}>

                    <p style={styles.metricLabel}>
                        Total Customers
                    </p>

                    <h2 style={styles.metricValue}>
                        {total_customers.toLocaleString()}
                    </h2>

                </div>


                {/* Total Churned */}

                <div style={styles.metricCard}>

                    <p style={styles.metricLabel}>
                        Total Churned
                    </p>

                    <h2 style={styles.metricValue}>
                        {churned.toLocaleString()}
                    </h2>

                </div>


                {/* Churn Rate */}

                <div style={styles.metricCard}>

                    <p style={styles.metricLabel}>
                        Churn Rate
                    </p>

                    <h2 style={styles.metricValue}>
                        {(churn_rate * 100).toFixed(1)}%
                    </h2>

                </div>

            </div>


            {/* =================================================
                CONTRACT CHURN
            ================================================= */}

            <div style={styles.section}>

                <h2>
                    Churn Rate by Contract Type
                </h2>


                <table style={styles.table}>

                    <thead>

                        <tr>

                            <th style={styles.th}>
                                Contract Type
                            </th>

                            <th style={styles.th}>
                                Churn Rate
                            </th>

                            <th style={styles.th}>
                                Comparison
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {by_contract.map((contract) => (

                            <tr key={contract.contract_type}>

                                <td style={styles.td}>
                                    {contract.contract_type}
                                </td>


                                <td style={styles.td}>

                                    {(contract.churn_rate * 100)
                                        .toFixed(1)}%

                                </td>


                                <td style={styles.td}>

                                    <div
                                        style={styles.barContainer}
                                    >

                                        <div
                                            style={{
                                                ...styles.bar,

                                                width: `${
                                                    contract.churn_rate * 100
                                                }%`
                                            }}
                                        />

                                    </div>

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>

    );

}


// ============================================================
// STYLES
// ============================================================

const styles = {

    container: {
        maxWidth: "1000px",
        margin: "40px auto",
        padding: "20px",
        fontFamily: "Arial, sans-serif"
    },


    description: {
        color: "#666",
        marginBottom: "30px"
    },


    metricsContainer: {
        display: "grid",
        gridTemplateColumns:
            "repeat(3, 1fr)",
        gap: "20px",
        marginBottom: "40px"
    },


    metricCard: {
        padding: "25px",
        border: "1px solid #ddd",
        borderRadius: "10px",
        boxShadow:
            "0 2px 8px rgba(0, 0, 0, 0.08)"
    },


    metricLabel: {
        margin: "0 0 10px 0",
        color: "#666",
        fontSize: "14px"
    },


    metricValue: {
        margin: 0,
        fontSize: "32px"
    },


    section: {
        marginTop: "30px"
    },


    table: {
        width: "100%",
        borderCollapse: "collapse",
        marginTop: "20px"
    },


    th: {
        textAlign: "left",
        padding: "14px",
        borderBottom: "2px solid #ddd"
    },


    td: {
        padding: "14px",
        borderBottom: "1px solid #eee"
    },


    barContainer: {
        width: "300px",
        height: "18px",
        backgroundColor: "#eee",
        borderRadius: "9px",
        overflow: "hidden"
    },


    bar: {
        height: "100%",
        backgroundColor: "#dc2626",
        borderRadius: "9px"
    },


    error: {
        marginTop: "20px",
        padding: "15px",
        borderRadius: "6px",
        backgroundColor: "#fee2e2",
        color: "#991b1b"
    }

};


export default ChurnSummary;