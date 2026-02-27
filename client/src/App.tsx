import { useCallback, useState, type ReactEventHandler } from 'react';
import './style.css'
import { useDropzone } from 'react-dropzone';

function App() {
  const [file, setFile] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: any) => {
    const url = URL.createObjectURL(acceptedFiles[0])

    setFile(url)
  }, []);

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
        </div>
        <button className='main__send-button'>Отправить</button>
      </div>
    </div>
  )
}

export default App
