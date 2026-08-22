// QuizBuilder.jsx


import {useEffect, useState} from 'react'
import {useFieldArray, useForm} from 'react-hook-form'
import {useNavigate, useParams} from 'react-router-dom'

import {apiCall, getHostQuizDetail, updateHostQuiz} from '../../api/api'

import QuestionEditor from './components/QuestionEditor'


export default function QuizBuilder() {

    const {quizId} = useParams()
    
    const navigate = useNavigate()

    const [activeQuestion, setActiveQuestion] = useState(0)
    const [isUploading, setIsUploading] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [errorMsg, setErrorMsg] = useState('')
    const [isLoadingData, setIsLoadingData] = useState(!!quizId)

    const emptyQuestion = {
        text : '',
        time_limit : 10,
        media_url : null,
        media_type : null,
        choices : [{text : '', is_correct : false}, {text : '', is_correct : false}, {text : '', is_correct : false}, {text : '', is_correct : false}]
    }

    const {register, control, handleSubmit, watch, setValue, reset} = useForm({defaultValues : {title : '', questions : [emptyQuestion]}})

    const {fields, append, remove} = useFieldArray({control, name : 'questions'})

    useEffect(() => {
        if (!quizId) return

        const fetchQuiz = async () => {
            try {
                const response = await getHostQuizDetail(quizId)

                if (response.ok) {
                    const data = await response.json()

                    reset(data) // Instantly populate the entire form, including nested IDs 
                } else {
                    setErrorMsg("Failed to load quiz data.")
                }
            } catch (err) {
                setErrorMsg("Failed to contact the server")
            } finally {
                setIsLoadingData(false)
            }
        }

        fetchQuiz()
    }, [quizId, reset])

    const onSubmit = async (data) => {
        setIsSubmitting(true)
        setErrorMsg('')
        
        // Filter out any choices where the text is empty or just whitespace
        const cleanedData = {...data, questions : data.questions.map(q => ({...q, choices : q.choices.filter(c => c.text.trim() !== '')}))}

        try {
            let response

            if (quizId) {
                response = await updateHostQuiz(quizId, cleanedData)
            } else {
                response = await apiCall('/quizzes/create/', {method : 'POST', body : JSON.stringify(cleanedData)})
            }

            const result = await response.json()

            if (response.ok) {
                navigate('/host/create-session')
            } else {
                setErrorMsg(`${result.error || JSON.stringify(result)}`)
            }
        } catch (error) {
            setErrorMsg("Failed to establish contact with the server.")
        } finally {
            setIsSubmitting(false)
        }
    }

    if (isLoadingData) {

        return (

            <div className = "p-8 text-ink font-mono font-bold text-2xl uppercase animate-pulse">
                Loading quiz architecture...
            </div>

        )

    }

    return (

        <form
            onSubmit = {handleSubmit(onSubmit)}
            className = "min-h-screen bg-bg-base p-4 md:p-8 text-ink flex gap-6 font-sans"
        >
            <div className = "w-1/4 flex flex-col gap-4">
                <input
                    type = 'text'
                    {...register('title', {required : true})}
                    placeholder = "QUIZ TITLE..."
                    className = "w-full bg-btn-neutral text-ink border-4 border-ink p-4 font-mono text-2xl font-bold uppercase shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow"
                />

                <div className = "flex-1 bg-card-dark border-4 border-ink shadow-brutal-lg p-4 flex flex-col gap-4 overflow-y-auto">
                    {fields.map((field, index) => (
                        <div
                            key = {field.id}
                            onClick = {() => setActiveQuestion(index)}
                            className = {`
                                p-4 border-4 border-ink cursor-pointer font-mono font-bold uppercase transition-transform
                                ${activeQuestion === index
                                    ? "bg-btn-neutral text-ink translate-x-2 shadow-brutal-sm"
                                    : "bg-bg-base text-ink hover:-translate-y-1 hover:shadow-brutal-sm"
                                }
                            `}
                        >
                            <div className = "flex justify-between items-center">
                                <span>Question {index + 1}</span>

                                {fields.length > 1 && (
                                    <button
                                        type = 'button'
                                        onClick = {(e) => {
                                            e.stopPropagation()

                                            remove(index)

                                            setActiveQuestion(Math.max(0, index - 1))
                                        }}
                                        className = "text-btn-wrong hover:text-ink px-2 text-xl transition-colors"
                                    >
                                        X
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                    
                    <button
                        type = 'button'
                        onClick = {() => {
                            append(emptyQuestion)

                            setActiveQuestion(fields.length)
                        }}
                        className = "p-4 border-4 border-ink bg-btn-correct text-ink font-bold uppercase shadow-brutal-sm hover:-translate-y-1 transition-all tracking-widest"
                    >
                        + Add Question
                    </button>
                </div>
            </div>

            <div className = "w-3/4 flex flex-col gap-6">
                {errorMsg && (
                    <div className = "bg-btn-wrong text-ink border-4 border-ink p-4 font-bold font-mono text-lg shadow-brutal-sm uppercase">
                        {errorMsg}
                    </div>
                )}

                <QuestionEditor
                    register = {register}
                    index = {activeQuestion}
                    watch = {watch}
                    setValue = {setValue}
                    setIsUploading = {setIsUploading}
                />

                <div className = "flex justify-end mt-4">
                    <button
                        type = 'submit'
                        disabled = {isUploading || isSubmitting}
                        className = "px-12 py-5 bg-ink text-text-inverted font-bold text-3xl uppercase border-4 border-ink shadow-brutal-md hover:-translate-y-1 hover:shadow-brutal-lg active:translate-y-1.5 active:translate-x-1.5 active:shadow-none disabled:opacity-50 disabled:pointer-events-none transition-all tracking-widest"
                    >
                        {isUploading ? (
                            "Uploading Media..."
                        ) : isSubmitting ? (
                            'Saving...'
                        ) : (
                            "Save Quiz"
                        )}
                    </button>
                </div>
            </div>
        </form>

    )

}