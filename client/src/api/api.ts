import axios from "axios";
import type { Detections } from "../types";

const instance = axios.create({
    baseURL: 'http://94.41.18.199:8080'
})

export const getPrediction = (file: File, setDetections: (detections: Detections) => void, setFile: (file: string) => void, setType: (type: string) => void) => {
    const formData = new FormData()

    formData.append('file', file)

    const res = instance.post('/predict', formData).then(res => {
        setDetections(res.data.detections)
        setType(res.data.type)

        const byteCharacters = atob(res.data.image_base64);
        const byteNumbers = new Array(byteCharacters.length);

        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);

        const mimeType = 'image/jpeg';

        const blob = new Blob([byteArray], { type: mimeType });
        const file = new File([blob], 'labeled_image', { type: mimeType });

        const url = URL.createObjectURL(file)

        setFile(url)
    })

    console.log(res);
    

    return res
}