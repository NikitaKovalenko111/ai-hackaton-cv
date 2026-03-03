export interface IDetection {
    class_name: string
    length_px: number
    length_cm: number
    area_px: number
    area_cm: number
    confidence: number
}

export type Detections = Array<IDetection>