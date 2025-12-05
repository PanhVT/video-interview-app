import { useRef, useState } from 'react'

export default function useRecorder() {
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const [recording, setRecording] = useState(false)
  const [stream, setStream] = useState(null)

  async function start(streamInstance) {
    if (!streamInstance) return
    chunksRef.current = []
    setStream(streamInstance)
    const options = { mimeType: 'video/webm;codecs=vp8,opus' }
    const mr = new MediaRecorder(streamInstance, options)
    mediaRecorderRef.current = mr
    mr.ondataavailable = e => { if (e.data && e.data.size) chunksRef.current.push(e.data) }
    mr.start()
    setRecording(true)
  }

  function stop() {
    return new Promise(resolve => {
      const mr = mediaRecorderRef.current
      if (!mr) return resolve(null)
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        chunksRef.current = []
        setRecording(false)
        resolve(blob)
      }
      mr.stop()
    })
  }

  function cleanup() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop())
      setStream(null)
    }
  }

  return { start, stop, cleanup, recording, stream }
}