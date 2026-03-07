import { useCallback, useRef, useState } from 'react';
import cn from 'classnames';
import './style.css'
import { useDropzone } from 'react-dropzone';
import type { ObjectsType } from './types';
import { getPrediction } from './api/api';
import preloader from './assets/1200x1200.gif'
import Popup from 'reactjs-popup';
import type { GalleryItem, ImageGalleryRef } from 'react-image-gallery';
import ImageGallery from 'react-image-gallery';
import "react-image-gallery/styles/image-gallery.css";
import { Toaster } from 'react-hot-toast';

function App() {
  const [files, setFiles] = useState<Array<GalleryItem>>([])
  const [byteFiles, setByteFiles] = useState<Array<File>>([])
  const [isVisible, setIsVisible] = useState<boolean>(false)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [objects, setObjects] = useState<ObjectsType>([])

  const onDrop = useCallback((acceptedFiles: Array<File>) => {
    const urls: Array<GalleryItem> = []

    acceptedFiles.forEach(file => {
      const url = URL.createObjectURL(file)

      urls.push({
        original: url,
        thumbnail: url
      })
    })

    setByteFiles(acceptedFiles)
    setFiles(urls)
  }, []);

  const sendHandler = async () => {
    if (byteFiles.length != 0) {
      setIsVisible(false)
      setIsLoading(true)
      await getPrediction(byteFiles, setObjects).then(() => {
        setIsVisible(true)
        setIsLoading(false)
      })
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const galleryRef = useRef<ImageGalleryRef>(null)

  return (
    <>
      {isLoading &&
        <div className="preloader">
          <img className='preloader__image' src={preloader} alt="Preloader" />
        </div>
      }
      <div className='container'>
        <Toaster 
          toastOptions={{
            style: {
              fontFamily: 'sans-serif'
            }
          }}
        />
        <div className="main">
          <div className="main__wrapper">
            <h1 className="main__header">Сегментация растений пшеницы и рукколы</h1>
            <Popup 
              on="hover"
              trigger={
              <button className='main__info-btn'>
                <span>!</span>
              </button>
              }
              mouseEnterDelay={100}
              mouseLeaveDelay={100}
              position="left top">
              <div className='main__popup'>
                <h2 className="main__popup-header">Информация о проекте и модели</h2>
                <p className='main__popup-text'>Проект создан в рамках хакатона "ИИ Хакатон УУНиТ". Модель по изображению рукколы/пшеницы автоматически определяет тип растения и вычисляет длины корня, стебля, лепестков</p>
                <span className='main__popup-label'>Модель: Yolo 26-seg</span>
                <span className='main__popup-label'>Метрики:</span>
                <div className='main__popup-metrics'>
                  <span>Box Precision: 0.963</span>
                  <span>Box Recall: 0.971</span>
                  <span>Box mAP50: 0.964</span>
                  <span>Box mAP50-95: 0.881</span>
                  <span>Mask Precision: 0.963</span>
                  <span>Mask Recall: 0.971</span>
                  <span>Mask mAP50: 0.962</span>
                  <span>Mask mAP50-95: 0.664</span>
                </div>
              </div>
            </Popup>
            {
              (files.length > 0 && isLoading) && (
                <img src={files[0].thumbnail} alt="preview" className='main__preview' />
              )
            }
            {
              (files.length > 0 && !isLoading) ? (
                <ImageGallery additionalClass='preview' ref={galleryRef} items={files} />
              ) : (files.length == 0) ? (
                <div className='main__empty-image'>
                  <span>
                    Изображение не выбрано
                  </span>
                </div>
              ) : ''
            }
            <div {...getRootProps()} className='main__dropzone'>
              <input {...getInputProps()} />
              {
                isDragActive ?
                  <p>Поместите изображения сюда</p> :
                  <p>Поместите сюда изображения или нажмите, чтобы выбрать</p>
              }
            </div>
            <button className='main__send-button' onClick={sendHandler}>Отправить</button>
          </div>
          {
            objects.map(obj => {
              return (
                <div className={cn('main__wrapper', 'main__params', { 'main__params--visible': isVisible })}>
                  <img className='main__prediction' width="400px" height="400px" src={obj.img} alt="Разметка изображения" />
                  <div className='main__labels-wrapper'>
                    <h2 className="main__header">Параметры</h2>
                    <div className="main__labels">
                      <div className="main__label">
                        <h3>Тип растения:</h3>
                        <span>{obj.type}</span>
                      </div>
                      {
                        obj.detections?.map(el => {
                          return (
                            <div className="main__label">
                              <h3>{el.class_name == 'root' ? 'Корень' : el.class_name == 'leaf' ? 'Лепесток' : el.class_name == 'stem' ? 'Стебель' : ''}</h3>
                              <div className="main__measures">
                                <span>Длина: {el.length_cm.toFixed(2)} см</span>
                                <span>Площадь: {el.area_cm.toFixed(2)} см<sup>2</sup></span>
                              </div>
                            </div>
                          )
                        })
                      }
                    </div>
                  </div>
                </div>
              )
            })
          }
        </div>
      </div>
    </>
  )
}

export default App
