import { useCallback, useState } from 'react';
import cn from 'classnames';
import './style.css'
import { useDropzone } from 'react-dropzone';
import type { Detections } from './types';
import { getPrediction } from './api/api';
import preloader from './assets/1200x1200.gif'
import infoIcon from './assets/info-icon.png'
import Popup from 'reactjs-popup';

function App() {
  const [file, setFile] = useState<string | null>(null)
  const [byteFile, setByteFile] = useState<File | null>(null)
  const [labeledFile, setLabeledFile] = useState<string | null>(null)
  const [isVisible, setIsVisible] = useState<boolean>(false)
  const [detections, setDetections] = useState<Detections | null>(null)
  const [type, setType] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const onDrop = useCallback((acceptedFiles: any) => {
    const url = URL.createObjectURL(acceptedFiles[0])

    setFile(url)
    setByteFile(acceptedFiles[0])
  }, []);

  const sendHandler = async () => {
    if (byteFile != null) {
      setIsVisible(false)
      setIsLoading(true)
      await getPrediction(byteFile, setDetections, setLabeledFile, setType).then(() => {
        setIsVisible(true)
        setIsLoading(false)
      })
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <>
    { isLoading &&
      <div className="preloader">
        <img className='preloader__image' src={preloader} alt="Preloader" />
      </div>
    }
    <div className='container'>
      <div className="main">
        <div className="main__wrapper">
          <h1 className="main__header">Сегментация растений пшеницы и рукколы</h1>
          <Popup trigger={<img className='main__popup-trigger' src={infoIcon}></img>} position="right center">
            <div className='main__popup'>
              <h2 className="main__popup-header">Информация о проекте и модели</h2>
              <p className='main__popup-text'>Проект создан в рамках хакатона "ИИ Хакатон УУНиТ". Модель по изображению рукколы/пшеницы автоматически определяет тип растения и вычисляет длины корня, стебля, лепестков</p>
              <span className='main__popup-label'>Модель: Yolo 26-seg</span>
              <span className='main__popup-label'>Метрики:</span>
              <div className='main__popup-metrics'>
                <span>Box Precision: 0.922</span>
                <span>Box Recall: 0.905</span>
                <span>Box mAP50: 0.946</span>
                <span>Box mAP50-95: 0.663</span>
                <span>Mask Precision: 0.85</span>
                <span>Mask Recall: 0.834</span>
                <span>Mask mAP50: 0.843</span>
                <span>Mask mAP50-95: 0.335</span>
              </div>
            </div>
          </Popup>
          {
            file != null ? (
              <img className='main__preview' src={file} alt="" />
            ) : (
              <div className='main__empty-image'>
                <span>
                  Изображение не выбрано
                </span>
              </div>
            )
          }
          <div {...getRootProps()} className='main__dropzone'>
            <input {...getInputProps()} />
            {
              isDragActive ?
              <p>Поместите изображение сюда</p> :
              <p>Поместите сюда изображение или нажмите, чтобы выбрать</p>
            }
          </div>
          <button className='main__send-button' onClick={sendHandler}>Отправить</button>
        </div>
        <div className={cn('main__wrapper', 'main__params', {'main__params--visible': isVisible})}>
          {
            labeledFile != null &&
            (
              <img className='main__prediction' width="400px" height="400px" src={labeledFile} alt="Разметка изображения" />
            )
          }
          <div className='main__labels-wrapper'>
            <h2 className="main__header">Параметры</h2>
            <div className="main__labels">
              <div className="main__label">
                <h3>Тип растения:</h3>
                <span>{type}</span>
              </div>
              {
                detections?.map(el => {
                  return (
                    <div className="main__label">
                      <h3>{el.class_name == 'root' ? 'Корень' : el.class_name == 'leaf' ? 'Лепесток' : el.class_name == 'stem' ? 'Стебель' : ''}</h3>
                      <div className="main__measures">
                        <span>Длина: {el.length_cm} см</span>
                        <span>Площадь: {el.area_cm} см^2</span>
                      </div>
                    </div>
                  )
                })
              }
            </div>
          </div>
        </div>
      </div>
    </div>
    </>
  )
}

export default App
