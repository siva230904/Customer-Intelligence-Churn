import { useState } from "react";
import api from "../api";


function CustomerSearch() {

    // ========================================================
    // STATE
    // ========================================================

    const [customerId, setCustomerId] = useState("");

    const [customer, setCustomer] = useState(null);

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");


    // ========================================================
    // SEARCH CUSTOMER
    // ========================================================

    const handleSearch = async () => {

        // ----------------------------------------------------
        // Basic validation
        // ----------------------------------------------------

        if (!customerId.trim()) {

            setError("Please enter a customer ID");

            setCustomer(null);

            return;
        }


        // ----------------------------------------------------
        // Reset previous state
        // ----------------------------------------------------

        setLoading(true);

        setError("");

        setCustomer(null);


        try {

            // ------------------------------------------------
            // GET /customer/{id}
            // ------------------------------------------------

            const response = await api.get(
                `/customer/${customerId.trim()}`
            );


            // ------------------------------------------------
            // Store customer data
            // ------------------------------------------------

            setCustomer(response.data);

        }

        catch (e) {

            // ------------------------------------------------
            // Customer not found
            // ------------------------------------------------

            if (e.response?.status === 404) {

                setError("Customer not found");

            }

            else if (e.response?.status === 401) {

                setError("Unauthorized. Check your API key.");

            }

            else {

                setError(
                    "Something went wrong while fetching the customer."
                );
            }

        }

        finally {

            setLoading(false);

        }
    };


    // ========================================================
    // HANDLE ENTER KEY
    // ========================================================

    const handleKeyDown = (e) => {

        if (e.key === "Enter") {

            handleSearch();

        }
    };


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div style={styles.container}>

            <h1>Customer Search</h1>

            <p style={styles.subtitle}>
                Search for a customer using their customer ID.
            </p>


            {/* =================================================
                SEARCH AREA
            ================================================= */}

            <div style={styles.searchContainer}>

                <input
                    type="text"
                    placeholder="Enter customer ID"
                    value={customerId}
                    onChange={(e) =>
                        setCustomerId(e.target.value)
                    }
                    onKeyDown={handleKeyDown}
                    style={styles.input}
                />


                <button
                    onClick={handleSearch}
                    disabled={loading}
                    style={styles.button}
                >
                    {loading ? "Searching..." : "Search"}
                </button>

            </div>


            {/* =================================================
                LOADING
            ================================================= */}

            {loading && (

                <p style={styles.loading}>
                    Loading customer...
                </p>

            )}


            {/* =================================================
                ERROR
            ================================================= */}

            {error && !loading && (

                <div style={styles.error}>
                    {error}
                </div>

            )}


            {/* =================================================
                CUSTOMER CARD
            ================================================= */}

            {customer && !loading && (

                <div style={styles.card}>

                    <h2>Customer Profile</h2>


                    <div style={styles.row}>

                        <span style={styles.label}>
                            Customer ID
                        </span>

                        <span>
                            {customer.customer_id}
                        </span>

                    </div>


                    <div style={styles.row}>

                        <span style={styles.label}>
                            Tenure
                        </span>

                        <span>
                            {customer.tenure} months
                        </span>

                    </div>


                    <div style={styles.row}>

                        <span style={styles.label}>
                            Contract
                        </span>

                        <span>
                            {customer.contract_type}
                        </span>

                    </div>


                    <div style={styles.row}>

                        <span style={styles.label}>
                            Internet Service
                        </span>

                        <span>
                            {customer.internet_service}
                        </span>

                    </div>


                    <div style={styles.row}>

                        <span style={styles.label}>
                            Monthly Charges
                        </span>

                        <span>
                            ${Number(
                                customer.monthly_charges
                            ).toFixed(2)}
                        </span>

                    </div>


                    {/* =========================================
                        CHURN STATUS
                    ========================================= */}

                    <div style={styles.row}>

                        <span style={styles.label}>
                            Churn Status
                        </span>


                        <span
                            style={{
                                ...styles.churnBadge,

                                backgroundColor:
                                    customer.churn === 1
                                        ? "#dc2626"
                                        : "#16a34a"
                            }}
                        >

                            {customer.churn === 1
                                ? "Churned"
                                : "Active"}

                        </span>

                    </div>

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

    subtitle: {
        color: "#666"
    },

    searchContainer: {
        display: "flex",
        gap: "10px",
        marginTop: "25px"
    },

    input: {
        flex: 1,
        padding: "12px",
        fontSize: "16px",
        border: "1px solid #ccc",
        borderRadius: "6px"
    },

    button: {
        padding: "12px 20px",
        fontSize: "16px",
        cursor: "pointer",
        border: "none",
        borderRadius: "6px"
    },

    loading: {
        marginTop: "20px"
    },

    error: {
        marginTop: "20px",
        padding: "15px",
        borderRadius: "6px",
        backgroundColor: "#fee2e2",
        color: "#991b1b"
    },

    card: {
        marginTop: "30px",
        padding: "25px",
        border: "1px solid #ddd",
        borderRadius: "10px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
    },

    row: {
        display: "flex",
        justifyContent: "space-between",
        padding: "14px 0",
        borderBottom: "1px solid #eee"
    },

    label: {
        fontWeight: "bold"
    },

    churnBadge: {
        color: "white",
        padding: "5px 12px",
        borderRadius: "15px",
        fontWeight: "bold"
    }
};


export default CustomerSearch;