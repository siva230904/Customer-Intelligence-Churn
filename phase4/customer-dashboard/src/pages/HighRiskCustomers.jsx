import { useEffect, useState } from "react";
import api from "../api";


function HighRiskCustomers() {

    // ========================================================
    // STATE
    // ========================================================

    const [customers, setCustomers] = useState([]);

    const [limit, setLimit] = useState(50);

    const [sortAsc, setSortAsc] = useState(true);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    // ========================================================
    // FETCH HIGH-RISK CUSTOMERS
    // ========================================================

    useEffect(() => {

        const fetchHighRiskCustomers = async () => {

            try {

                setLoading(true);

                setError("");


                const response = await api.get(
                    "/customers/high-risk",
                    {
                        params: {
                            limit: limit
                        }
                    }
                );


                console.log(
                    "High-Risk Customers:",
                    response.data
                );


                setCustomers(response.data);

            }

            catch (e) {

                console.error(
                    "High-Risk API Error:",
                    e
                );


                if (e.response?.status === 401) {

                    setError(
                        "Unauthorized. Please check your API key."
                    );

                }

                else {

                    setError(
                        "Failed to load high-risk customers."
                    );

                }

            }

            finally {

                setLoading(false);

            }

        };


        fetchHighRiskCustomers();

    }, [limit]);


    // ========================================================
    // SORT BY TENURE
    // ========================================================

    const sortedCustomers = [...customers].sort(
        (a, b) => {

            if (sortAsc) {

                return a.tenure - b.tenure;

            }

            return b.tenure - a.tenure;

        }
    );


    // ========================================================
    // TOGGLE SORT
    // ========================================================

    const handleTenureSort = () => {

        setSortAsc((previous) => !previous);

    };


    // ========================================================
    // LOAD MORE
    // ========================================================

    const handleLoadMore = () => {

        setLimit((previous) => previous + 50);

    };


    // ========================================================
    // LOADING
    // ========================================================

    if (loading && customers.length === 0) {

        return (

            <div style={styles.container}>

                <h1>High-Risk Customers</h1>

                <p>Loading high-risk customers...</p>

            </div>

        );

    }


    // ========================================================
    // ERROR
    // ========================================================

    if (error && customers.length === 0) {

        return (

            <div style={styles.container}>

                <h1>High-Risk Customers</h1>

                <div style={styles.error}>
                    {error}
                </div>

            </div>

        );

    }


    // ========================================================
    // EMPTY RESULT
    // ========================================================

    if (
        !loading &&
        customers.length === 0
    ) {

        return (

            <div style={styles.container}>

                <h1>High-Risk Customers</h1>

                <div style={styles.empty}>
                    No high-risk customers found
                </div>

            </div>

        );

    }


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div style={styles.container}>

            {/* =================================================
                HEADER
            ================================================= */}

            <h1>High-Risk Customers</h1>

            <p style={styles.description}>
                Customers flagged by the rule-based retention
                risk criteria.
            </p>


            {/* =================================================
                COUNT BANNER
            ================================================= */}

            <div style={styles.banner}>

                {customers.length} high-risk customers identified

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div style={styles.error}>
                    {error}
                </div>

            )}


            {/* =================================================
                TABLE
            ================================================= */}

            <div style={styles.tableWrapper}>

                <table style={styles.table}>

                    <thead>

                        <tr>

                            <th style={styles.th}>
                                Customer ID
                            </th>


                            <th
                                style={{
                                    ...styles.th,
                                    ...styles.sortable
                                }}

                                onClick={
                                    handleTenureSort
                                }
                            >

                                Tenure

                                <span
                                    style={
                                        styles.sortIcon
                                    }
                                >

                                    {sortAsc
                                        ? " ↑"
                                        : " ↓"}

                                </span>

                            </th>


                            <th style={styles.th}>
                                Monthly Charges
                            </th>


                            <th style={styles.th}>
                                Contract Type
                            </th>


                            <th style={styles.th}>
                                Risk Reason
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {sortedCustomers.map(
                            (customer) => (

                                <tr
                                    key={
                                        customer.customer_id
                                    }
                                >

                                    <td style={styles.td}>
                                        {customer.customer_id}
                                    </td>


                                    <td style={styles.td}>
                                        {customer.tenure}
                                    </td>


                                    <td style={styles.td}>

                                        $
                                        {Number(
                                            customer.monthly_charges
                                        ).toFixed(2)}

                                    </td>


                                    <td style={styles.td}>
                                        {customer.contract_type}
                                    </td>


                                    <td style={styles.td}>
                                        {customer.risk_reason}
                                    </td>

                                </tr>

                            )
                        )}

                    </tbody>

                </table>

            </div>


            {/* =================================================
                LOAD MORE
            ================================================= */}

            <div style={styles.loadMoreContainer}>

                <button
                    onClick={handleLoadMore}
                    disabled={loading}
                    style={styles.button}
                >

                    {loading
                        ? "Loading..."
                        : "Load More"}

                </button>

            </div>

        </div>

    );

}


// ============================================================
// STYLES
// ============================================================

const styles = {

    container: {
        maxWidth: "1200px",
        margin: "40px auto",
        padding: "20px",
        fontFamily: "Arial, sans-serif"
    },


    description: {
        color: "#666",
        marginBottom: "25px"
    },


    banner: {
        padding: "15px 20px",
        marginBottom: "25px",
        borderRadius: "8px",
        backgroundColor: "#f3f4f6",
        fontWeight: "bold"
    },


    tableWrapper: {
        overflowX: "auto"
    },


    table: {
        width: "100%",
        borderCollapse: "collapse"
    },


    th: {
        textAlign: "left",
        padding: "14px",
        borderBottom: "2px solid #ddd",
        backgroundColor: "#f9fafb"
    },


    sortable: {
        cursor: "pointer",
        userSelect: "none"
    },


    sortIcon: {
        fontWeight: "bold",
        marginLeft: "5px"
    },


    td: {
        padding: "14px",
        borderBottom: "1px solid #eee"
    },


    loadMoreContainer: {
        display: "flex",
        justifyContent: "center",
        marginTop: "25px"
    },


    button: {
        padding: "12px 25px",
        border: "none",
        borderRadius: "6px",
        cursor: "pointer",
        fontSize: "16px"
    },


    error: {
        padding: "15px",
        marginBottom: "20px",
        borderRadius: "6px",
        backgroundColor: "#fee2e2",
        color: "#991b1b"
    },


    empty: {
        padding: "30px",
        textAlign: "center",
        border: "1px solid #ddd",
        borderRadius: "8px",
        marginTop: "25px",
        color: "#666"
    }

};


export default HighRiskCustomers;