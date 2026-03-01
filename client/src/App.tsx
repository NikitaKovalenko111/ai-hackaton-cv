import { useCallback, useState, type ReactEventHandler } from 'react';
import cn from 'classnames';
import './style.css'
import { useDropzone } from 'react-dropzone';
import img from './assets/wheat_20260219161454681.jpg'

function App() {
  const [file, setFile] = useState<string | null>(null)
  const [isVisible, setIsVisible] = useState<boolean>(false)

  const onDrop = useCallback((acceptedFiles: any) => {
    const url = URL.createObjectURL(acceptedFiles[0])

    setFile(url)
  }, []);

  const sendHandler = () => {
    setIsVisible(true)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div className='container'>
      <div className="main">
        <div className="main__wrapper">
          <h1 className="main__header">Сегментация растений пшеницы и рукколы</h1>
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
          <img className='main__prediction' width="400px" src={img} alt="Разметка изображения" />
          <div>
            <h2 className="main_header">Параметры</h2>
            <div className="main__labels">
              <div className="main__label">
                <h3>Тип растения:</h3>
                <span>Пшеница</span>
              </div>
              <div className="main__label">
                <h3>Длина корня:</h3>
                <span>5 см</span>
              </div>
              <div className="main__label">
                <h3>Длина стебля:</h3>
                <span>6 см</span>
              </div>
              <div className="main__label">
                <h3>Площадь листиков:</h3>
                <span>12 см^2</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
