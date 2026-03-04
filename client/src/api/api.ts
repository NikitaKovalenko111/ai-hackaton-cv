import axios from "axios";
import type { ObjectsType } from "../types";

const instance = axios.create({
    baseURL: 'http://94.41.18.199:8080'
})

export const getPrediction = (files: Array<File>, setObjects: (objects: ObjectsType) => void) => {
    const formData = new FormData()

    files.forEach(file => {
        formData.append('files', file)
    })

    const res = instance.post('/predict', formData).then(res => {
        const objects: ObjectsType = []

        res.data.forEach((obj: any) => {
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

            objects.push({
                detections: obj.detections,
                type: obj.type,
                img: url
            })

            setObjects(objects)
        })
    })


    return res
}