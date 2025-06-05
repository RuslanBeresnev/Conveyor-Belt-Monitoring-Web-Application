export default class AuthenticationUtils {
    static isTokenExpired = (token) => {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url
                .replace(/-/g, '+')
                .replace(/_/g, '/')
                .padEnd(base64Url.length + (4 - base64Url.length % 4) % 4, '=');
            const payload = JSON.parse(atob(base64));
            const exp = payload.exp * 1000;
            return Date.now() > exp;
        } catch {
            return true;
        }
    };

    static checkAuth = () => {
        const token = localStorage.getItem('access_token');
        return token && !AuthenticationUtils.isTokenExpired(token);
    };

    static login = (token) => {
        localStorage.setItem('access_token', token);
        window.location.href = '/defects';
    }

    static logout = (redirectToAuth = true) => {
        localStorage.removeItem('access_token');
        if (redirectToAuth) window.location.href = '/auth';
    };
}
