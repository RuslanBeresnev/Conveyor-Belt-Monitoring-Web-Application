import { useState } from "react";
import { Navigate } from "react-router-dom";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import { useAuth } from "../../context/AuthenticationContext";
import AuthenticationService from "../../API/AuthenticationService";

export default function Authentication() {
    const { checkAuth, login } = useAuth();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleLogin = async (e) => {
        e.preventDefault();
        await AuthenticationService.loginAndGetToken(username, password)
            .then(response => login(response.data.access_token))
            .catch(error => {
                if (!error.response) setError("Server unavailable");
                else setError("Incorrect username or password");
            })
    };

    if (checkAuth()) {
        return <Navigate to="/defects" replace />;
    }

    return (
        <Box sx={{ maxWidth: 400, mx: 'auto', mt: 10 }}>
            <Typography variant='h5' gutterBottom>Authentication</Typography>
            {error && <Alert severity='error'>{error}</Alert>}
            <form onSubmit={handleLogin}>
                <TextField
                    label='Login'
                    fullWidth
                    margin='normal'
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <TextField
                    label='Password'
                    type='password'
                    fullWidth
                    margin='normal'
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    fullWidth
                    sx={{ mt: 2 }}
                >
                    Enter to system
                </Button>
            </form>
        </Box>
    );
};
