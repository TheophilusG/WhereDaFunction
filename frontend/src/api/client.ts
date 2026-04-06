import axios from 'axios';
const baseURL = process.env.EXPO_PUBLIC_API_BASE_URL;


if (!baseURL) {
    throw new Error('Missing EXPO_PUBLIC_API_BASE_URL');

}

export const api = axios.create({
    baseURL,
    timeout: 10000,
});