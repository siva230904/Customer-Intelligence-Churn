import {
    BrowserRouter,
    Routes,
    Route,
    NavLink
} from "react-router-dom";

import CustomerSearch from "./pages/CustomerSearch";
import ChurnSummary from "./pages/ChurnSummary";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";


function App() {

    return (

        <BrowserRouter>

            {/* =================================================
                NAVIGATION BAR
            ================================================= */}

            <nav style={styles.nav}>

                <h2 style={styles.logo}>
                    Customer 360
                </h2>


                <div style={styles.links}>

                    <NavLink
                        to="/"
                        style={navStyle}
                    >
                        Churn Summary
                    </NavLink>


                    <NavLink
                        to="/customer-search"
                        style={navStyle}
                    >
                        Customer Search
                    </NavLink>


                    <NavLink
                        to="/high-risk"
                        style={navStyle}
                    >
                        High-Risk Customers
                    </NavLink>


                    <NavLink
                        to="/predict"
                        style={navStyle}
                    >
                        Churn Prediction
                    </NavLink>

                </div>

            </nav>


            {/* =================================================
                ROUTES
            ================================================= */}

            <Routes>

                <Route
                    path="/"
                    element={<ChurnSummary />}
                />


                <Route
                    path="/customer-search"
                    element={<CustomerSearch />}
                />


                <Route
                    path="/high-risk"
                    element={<HighRiskCustomers />}
                />


                <Route
                    path="/predict"
                    element={<ChurnPrediction />}
                />

            </Routes>

        </BrowserRouter>

    );

}


// ============================================================
// NAVIGATION STYLE
// ============================================================

const navStyle = ({ isActive }) => ({

    textDecoration: "none",

    padding: "10px 15px",

    borderRadius: "6px",

    color: isActive
        ? "white"
        : "#333",

    backgroundColor: isActive
        ? "#2563eb"
        : "transparent",

    fontWeight: isActive
        ? "bold"
        : "normal"

});


// ============================================================
// PAGE STYLES
// ============================================================

const styles = {

    nav: {

        display: "flex",

        alignItems: "center",

        justifyContent: "space-between",

        padding: "15px 30px",

        borderBottom: "1px solid #ddd",

        backgroundColor: "#ffffff"

    },


    logo: {

        margin: 0

    },


    links: {

        display: "flex",

        gap: "10px",

        alignItems: "center"

    }

};


export default App;